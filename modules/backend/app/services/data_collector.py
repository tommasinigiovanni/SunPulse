"""
Data Collector Service - Raccolta automatica dati ZCS con Celery
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery import Celery
from celery.schedules import crontab
import structlog

from ..config.settings import get_settings
from ..services.zcs_api_service import get_zcs_service
from ..services.cache_service import get_cache_service, DataType, make_device_cache_key
from ..models.device import parse_zcs_realtime_to_models, DeviceDataPoint
from ..config.settings import get_settings

logger = structlog.get_logger()

# Configurazione Celery
settings = get_settings()

celery_app = Celery(
    'sunpulse',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.services.data_collector']
)

# Configurazione Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_send_events=True,
    worker_send_task_events=True,
    result_expires=3600,  # Results expire after 1 hour
    
    # RedBeat configurazione per Redis scheduler
    redbeat_redis_url=settings.redis_url,
    redbeat_key_prefix='sunpulse',
    redbeat_lock_timeout=300,
)

# Configurazione scheduler
celery_app.conf.beat_schedule = {
    # Raccolta dati realtime ogni 2 minuti
    'collect-realtime-data': {
        'task': 'app.services.data_collector.collect_realtime_data',
        'schedule': 120.0,  # 2 minuti
    },
    
    # Raccolta allarmi ogni 30 secondi
    'collect-alarm-data': {
        'task': 'app.services.data_collector.collect_alarm_data', 
        'schedule': 30.0,  # 30 secondi
    },
    
    # Health check ogni 5 minuti
    'health-check': {
        'task': 'app.services.data_collector.health_check_task',
        'schedule': 300.0,  # 5 minuti
    },
    
    # Raccolta energia giornaliera alle 00:05 ogni giorno
    'collect-daily-energy': {
        'task': 'app.services.data_collector.collect_daily_energy',
        'schedule': crontab(hour=0, minute=5),  # 00:05 UTC
    },
    
    # Pulizia cache vecchia alle 03:00 ogni giorno
    'cleanup-old-cache': {
        'task': 'app.services.data_collector.cleanup_old_cache',
        'schedule': crontab(hour=3, minute=0),  # 03:00 UTC
    },
    
    # Report giornaliero email alle 20:00 (19:00 UTC in inverno, 18:00 UTC in estate)
    'send-daily-email-report': {
        'task': 'app.services.data_collector.send_daily_email_report',
        'schedule': crontab(hour=19, minute=0),  # 19:00 UTC = 20:00 CET
    },
    
    # Report settimanale email domenica alle 10:00 (09:00 UTC)
    'send-weekly-email-report': {
        'task': 'app.services.data_collector.send_weekly_email_report',
        'schedule': crontab(hour=9, minute=0, day_of_week=0),  # Domenica 09:00 UTC = 10:00 CET
    },
}

class DataCollectionError(Exception):
    """Errore durante la raccolta dati"""
    pass

@celery_app.task(bind=True, max_retries=3)
def collect_realtime_data(self):
    """Task Celery: Raccolta dati realtime per tutti i dispositivi attivi"""
    task_id = self.request.id
    start_time = datetime.utcnow()
    
    logger.info("Starting realtime data collection", task_id=task_id)
    
    try:
        result = asyncio.run(_collect_realtime_data_async())
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            "Realtime data collection completed",
            task_id=task_id,
            duration_seconds=duration,
            **result
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Realtime data collection failed",
            task_id=task_id,
            error=str(e),
            retry_count=self.request.retries
        )
        
        countdown = 2 ** self.request.retries
        raise self.retry(exc=e, countdown=countdown, max_retries=3)

async def _collect_realtime_data_async() -> Dict[str, Any]:
    """Implementazione async della raccolta dati realtime"""
    zcs_service = await get_zcs_service()
    cache_service = await get_cache_service()
    
    # Ottieni dispositivi configurati
    settings = get_settings()
    thing_keys = settings.device_thing_keys
    
    if not thing_keys:
        logger.warning("No device thingKeys configured")
        return {
            "devices_processed": 0,
            "total_data_points": 0,
            "errors": 1,
            "error_message": "No devices configured"
        }
    
    # Ottieni dati realtime da ZCS API
    zcs_result = await zcs_service.get_realtime_data(thing_keys)
    
    if not zcs_result.get('success'):
        raise DataCollectionError(f"ZCS API failed: {zcs_result.get('error')}")
    
    processed_devices = 0
    total_data_points = 0
    errors = 0
    
    # Processa dati per ogni dispositivo
    for thing_key in thing_keys:
        try:
            device_data = zcs_result['data'].get(thing_key)
            
            if device_data:
                # Converte dati ZCS in data points
                data_points = parse_zcs_realtime_to_models(device_data, thing_key)
                
                if data_points:
                    total_data_points += len(data_points)
                    
                    # Cache dati per API frontend
                    cache_key = make_device_cache_key(thing_key, DataType.REALTIME)
                    await cache_service.set(cache_key, device_data, DataType.REALTIME)
                
                processed_devices += 1
            
        except Exception as e:
            logger.error(
                "Error processing device data",
                thing_key=thing_key,
                error=str(e)
            )
            errors += 1
    
    return {
        "devices_processed": processed_devices,
        "total_data_points": total_data_points,
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat()
    }

@celery_app.task(bind=True, max_retries=2)
def collect_alarm_data(self):
    """Task Celery: Raccolta allarmi per tutti i dispositivi attivi e invio notifiche"""
    task_id = self.request.id
    logger.info("Starting alarm data collection", task_id=task_id)
    
    try:
        result = asyncio.run(_collect_alarm_data_async())
        logger.info("Alarm data collection completed", task_id=task_id, **result)
        return result
        
    except Exception as e:
        logger.error("Alarm data collection failed", task_id=task_id, error=str(e))
        return {"devices_processed": 0, "alarms_found": 0, "errors": 1, "error": str(e)}


async def _collect_alarm_data_async() -> Dict[str, Any]:
    """Implementazione async della raccolta allarmi con notifiche email"""
    from ..services.email_service import get_email_service
    from ..services.database import get_db_session
    from ..models.settings import UserSettings
    from sqlalchemy import select
    
    settings = get_settings()
    thing_keys = settings.device_thing_keys
    zcs_service = await get_zcs_service()
    cache_service = await get_cache_service()
    email_service = get_email_service()
    
    devices_processed = 0
    alarms_found = 0
    emails_sent = 0
    errors = 0
    
    # Cache key per tracciare allarmi già notificati
    NOTIFIED_ALARMS_KEY = "alarms:notified"
    
    for thing_key in thing_keys:
        try:
            # Ottieni allarmi da ZCS
            alarm_data = await zcs_service.get_alarm_data([thing_key])
            devices_processed += 1
            
            if not alarm_data or not alarm_data.get("success"):
                continue
            
            device_alarms = alarm_data.get("data", {}).get(thing_key, {})
            current_alarms = device_alarms.get("alarms", [])
            
            if not current_alarms:
                continue
            
            alarms_found += len(current_alarms)
            
            # Controlla se ci sono nuovi allarmi critici da notificare
            for alarm in current_alarms:
                alarm_code = alarm.get("code", "UNKNOWN")
                alarm_id = f"{thing_key}:{alarm_code}"
                
                # Verifica se già notificato (evita spam)
                already_notified = await cache_service.redis.sismember(NOTIFIED_ALARMS_KEY, alarm_id)
                if already_notified:
                    continue
                
                # Determina severità
                severity = "warning"
                alarm_level = alarm.get("level", "").lower()
                if "critical" in alarm_level or "error" in alarm_level or alarm.get("priority", 0) >= 3:
                    severity = "critical"
                elif "info" in alarm_level:
                    severity = "info"
                
                # Invia notifiche solo per allarmi critici o warning
                if severity in ["critical", "warning"] and email_service.is_configured:
                    try:
                        # Ottieni utenti che vogliono notifiche
                        async with get_db_session() as db:
                            notify_field = UserSettings.notify_critical_alarms if severity == "critical" else UserSettings.notify_warnings
                            result = await db.execute(
                                select(UserSettings).where(
                                    notify_field == True,
                                    UserSettings.notification_email.isnot(None)
                                )
                            )
                            users_to_notify = result.scalars().all()
                        
                        for user in users_to_notify:
                            email_result = await email_service.send_alarm_notification(
                                alarm_type=alarm.get("type", alarm_code),
                                alarm_message=alarm.get("message", f"Allarme {alarm_code} rilevato"),
                                device_name=f"Dispositivo {thing_key[-4:]}",
                                severity=severity,
                                to_email=user.notification_email
                            )
                            if email_result.get("success"):
                                emails_sent += 1
                        
                        # Marca come notificato (scade dopo 24 ore)
                        await cache_service.redis.sadd(NOTIFIED_ALARMS_KEY, alarm_id)
                        await cache_service.redis.expire(NOTIFIED_ALARMS_KEY, 86400)
                        
                    except Exception as e:
                        logger.error("Error sending alarm notification", alarm_id=alarm_id, error=str(e))
                        errors += 1
                        
        except Exception as e:
            logger.error("Error processing device alarms", thing_key=thing_key, error=str(e))
            errors += 1
    
    return {
        "devices_processed": devices_processed,
        "alarms_found": alarms_found,
        "emails_sent": emails_sent,
        "errors": errors
    }


@celery_app.task
def health_check_task():
    """Task Celery: Health check completo del sistema"""
    logger.info("Starting system health check")
    
    try:
        result = asyncio.run(_health_check_async())
        logger.info("System health check completed", **result)
        return result
        
    except Exception as e:
        logger.error("System health check failed", error=str(e))
        return {"healthy": False, "error": str(e)}

async def _health_check_async() -> Dict[str, Any]:
    """Implementazione async del health check"""
    try:
        # Check ZCS API
        zcs_service = await get_zcs_service()
        zcs_health = await zcs_service.health_check()
        
        # Check cache
        cache_service = await get_cache_service()
        cache_stats = cache_service.get_stats()
        
        return {
            "healthy": True,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "zcs_api": zcs_health,
                "cache": {
                    "healthy": cache_stats["redis_connected"],
                    "hit_rate": cache_stats["hit_rate_percent"],
                    "total_requests": cache_stats["total_requests"]
                }
            }
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True, max_retries=3)
def collect_daily_energy(self):
    """
    Task Celery: Raccolta e persistenza energia giornaliera
    
    Eseguito ogni giorno alle 00:05 per salvare i dati del giorno precedente.
    Calcola l'energia giornaliera dalla differenza dei contatori TotalDecimal.
    """
    task_id = self.request.id
    start_time = datetime.utcnow()
    
    logger.info("Starting daily energy collection", task_id=task_id)
    
    try:
        result = asyncio.run(_collect_daily_energy_async())
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            "Daily energy collection completed",
            task_id=task_id,
            duration_seconds=duration,
            **result
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Daily energy collection failed",
            task_id=task_id,
            error=str(e),
            retry_count=self.request.retries
        )
        
        countdown = 60 * (2 ** self.request.retries)  # Retry dopo 1, 2, 4 minuti
        raise self.retry(exc=e, countdown=countdown, max_retries=3)


async def _collect_daily_energy_async() -> Dict[str, Any]:
    """Implementazione async della raccolta energia giornaliera"""
    from ..services.database import get_db_session
    from ..models.device import DailyEnergy
    from sqlalchemy import select
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    
    zcs_service = await get_zcs_service()
    settings = get_settings()
    thing_keys = settings.device_thing_keys
    
    if not thing_keys:
        return {"devices_processed": 0, "error": "No devices configured"}
    
    # Calcola il giorno precedente
    yesterday = (datetime.utcnow() - timedelta(days=1)).date()
    yesterday_start = datetime.combine(yesterday, datetime.min.time())
    yesterday_end = datetime.combine(yesterday, datetime.max.time())
    
    logger.info("Collecting daily energy", date=str(yesterday), thing_keys=thing_keys)
    
    # Ottieni dati storici dal giorno precedente
    hist_result = await zcs_service.get_historic_data(
        thing_keys, 
        yesterday_start, 
        yesterday_end, 
        "1h"
    )
    
    if not hist_result.get('success'):
        raise DataCollectionError(f"ZCS API failed: {hist_result.get('error')}")
    
    processed = 0
    errors = 0
    
    async with get_db_session() as session:
        for thing_key in thing_keys:
            try:
                device_data = hist_result['data'].get(thing_key)
                if not device_data:
                    continue
                
                hist = device_data.get('historicData', {}).get('params', {}).get('value', [])
                if not hist or len(hist) == 0:
                    continue
                
                zcs = hist[0].get(thing_key, {})
                
                # Calcola energie dalla differenza dei TotalDecimal
                field_mapping = {
                    "energyGeneratingTotalDecimal": "energy_generating",
                    "energyConsumingTotalDecimal": "energy_consuming",
                    "energyAutoconsumingTotalDecimal": "energy_autoconsuming",
                    "energyImportingTotalDecimal": "energy_importing",
                    "energyExportingTotalDecimal": "energy_exporting",
                    "energyChargingTotalDecimal": "energy_charging",
                    "energyDischargingTotalDecimal": "energy_discharging",
                }
                
                daily_data = {
                    "device_thing_key": thing_key,
                    "date": yesterday,
                }
                
                for zcs_field, db_field in field_mapping.items():
                    vals = zcs.get(zcs_field, [])
                    if isinstance(vals, list) and len(vals) >= 2:
                        first = vals[0] if vals[0] else 0
                        last = vals[-1] if vals[-1] else 0
                        daily_data[db_field] = max(0, last - first)
                    else:
                        daily_data[db_field] = 0
                
                # Salva contatori totali per verifica
                gen_total = zcs.get("energyGeneratingTotalDecimal", [])
                cons_total = zcs.get("energyConsumingTotalDecimal", [])
                if gen_total and len(gen_total) > 0:
                    daily_data["energy_generating_total"] = gen_total[-1]
                if cons_total and len(cons_total) > 0:
                    daily_data["energy_consuming_total"] = cons_total[-1]
                
                # Upsert in database
                stmt = pg_insert(DailyEnergy).values(**daily_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['device_thing_key', 'date'],
                    set_=daily_data
                )
                await session.execute(stmt)
                
                processed += 1
                
                logger.debug(
                    "Daily energy saved",
                    thing_key=thing_key,
                    date=str(yesterday),
                    generating=daily_data.get("energy_generating", 0),
                    consuming=daily_data.get("energy_consuming", 0)
                )
                
            except Exception as e:
                logger.error("Error processing device daily energy", thing_key=thing_key, error=str(e))
                errors += 1
        
        await session.commit()
    
    return {
        "devices_processed": processed,
        "errors": errors,
        "date": str(yesterday),
        "timestamp": datetime.utcnow().isoformat()
    }


@celery_app.task
def cleanup_old_cache(self=None):
    """
    Task Celery: Pulizia cache vecchia
    
    Eseguito ogni notte alle 03:00 per rimuovere dati cached obsoleti.
    """
    logger.info("Starting cache cleanup")
    
    try:
        result = asyncio.run(_cleanup_cache_async())
        logger.info("Cache cleanup completed", **result)
        return result
        
    except Exception as e:
        logger.error("Cache cleanup failed", error=str(e))
        return {"success": False, "error": str(e)}


async def _cleanup_cache_async() -> Dict[str, Any]:
    """Implementazione async della pulizia cache"""
    cache_service = await get_cache_service()
    
    # Invalida pattern vecchi
    patterns_to_clean = [
        "device:realtime:*",
        "device:historic:*",
        "system:realtime:*",
    ]
    
    total_invalidated = 0
    for pattern in patterns_to_clean:
        try:
            count = await cache_service.invalidate_pattern(pattern)
            total_invalidated += count
        except Exception as e:
            logger.warning("Error cleaning pattern", pattern=pattern, error=str(e))
    
    return {
        "success": True,
        "invalidated_keys": total_invalidated,
        "timestamp": datetime.utcnow().isoformat()
    }


def get_task_status(task_id: str) -> Dict[str, Any]:
    """Ottieni status di un task Celery"""
    try:
        result = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
            "traceback": result.traceback,
            "date_done": result.date_done
        }
        
    except Exception as e:
        return {
            "task_id": task_id,
            "status": "ERROR",
            "error": str(e)
        }


# ==============================================================================
# EMAIL REPORT TASKS
# ==============================================================================

@celery_app.task(bind=True, max_retries=2)
def send_daily_email_report(self):
    """
    Task Celery: Invia report giornaliero via email
    
    Eseguito ogni sera alle 20:00 per gli utenti che hanno abilitato notify_daily_report.
    """
    task_id = self.request.id
    logger.info("Starting daily email report", task_id=task_id)
    
    try:
        result = asyncio.run(_send_daily_email_report_async())
        logger.info("Daily email report completed", task_id=task_id, **result)
        return result
        
    except Exception as e:
        logger.error("Daily email report failed", task_id=task_id, error=str(e))
        raise self.retry(countdown=300, exc=e)  # Retry dopo 5 minuti


async def _send_daily_email_report_async() -> Dict[str, Any]:
    """Implementazione async del report giornaliero"""
    from ..services.email_service import get_email_service
    from ..services.database import get_db_session
    from ..models.settings import UserSettings
    from sqlalchemy import select
    
    email_service = get_email_service()
    if not email_service.is_configured:
        return {"success": False, "error": "Email service not configured", "sent": 0}
    
    emails_sent = 0
    errors = []
    
    try:
        # Ottieni tutti gli utenti con report giornaliero abilitato
        async with get_db_session() as db:
            result = await db.execute(
                select(UserSettings).where(
                    UserSettings.notify_daily_report == True,
                    UserSettings.notification_email.isnot(None)
                )
            )
            users_with_daily_report = result.scalars().all()
        
        if not users_with_daily_report:
            logger.info("No users with daily report enabled")
            return {"success": True, "sent": 0, "message": "No users with daily report enabled"}
        
        # Ottieni dati energia del giorno
        zcs_service = await get_zcs_service()
        settings = get_settings()
        thing_keys = settings.device_thing_keys
        
        # Aggregato giornaliero
        total_production = 0
        total_consumption = 0
        total_self_consumption = 0
        total_from_grid = 0
        total_to_grid = 0
        
        for thing_key in thing_keys:
            try:
                realtime = await zcs_service.get_realtime_data([thing_key])
                if realtime and realtime.get("success"):
                    data = realtime.get("data", {}).get(thing_key, {})
                    rt_data = data.get("realtimeData", {})
                    
                    total_production += float(rt_data.get("generatingTodayEnergy", 0) or 0)
                    total_consumption += float(rt_data.get("consumingTodayEnergy", 0) or 0)
                    total_self_consumption += float(rt_data.get("autoConsumingEnergy", 0) or 0)
                    total_from_grid += float(rt_data.get("importingEnergy", 0) or 0)
                    total_to_grid += float(rt_data.get("exportingEnergy", 0) or 0)
            except Exception as e:
                logger.warning("Error getting data for device", thing_key=thing_key, error=str(e))
        
        # Invia email a ogni utente
        for user_settings in users_with_daily_report:
            try:
                # Calcola risparmio con tariffe utente
                energy_price = user_settings.energy_price or 0.25
                sell_price = user_settings.sell_price or 0.10
                savings = (total_self_consumption * energy_price) + (total_to_grid * sell_price)
                
                result = await email_service.send_daily_report(
                    production_kwh=total_production,
                    consumption_kwh=total_consumption,
                    self_consumption_kwh=total_self_consumption,
                    from_grid_kwh=total_from_grid,
                    to_grid_kwh=total_to_grid,
                    savings_eur=savings,
                    to_email=user_settings.notification_email,
                    system_name=user_settings.system_name or "Il mio impianto"
                )
                
                if result.get("success"):
                    emails_sent += 1
                else:
                    errors.append(f"User {user_settings.user_id}: {result.get('error')}")
                    
            except Exception as e:
                errors.append(f"User {user_settings.user_id}: {str(e)}")
        
        return {
            "success": True,
            "sent": emails_sent,
            "errors": errors if errors else None,
            "production_kwh": total_production
        }
        
    except Exception as e:
        logger.error("Error in daily email report", error=str(e))
        return {"success": False, "error": str(e), "sent": emails_sent}


@celery_app.task(bind=True, max_retries=2)
def send_weekly_email_report(self):
    """
    Task Celery: Invia report settimanale via email
    
    Eseguito ogni domenica alle 10:00 per gli utenti che hanno abilitato notify_weekly_report.
    """
    task_id = self.request.id
    logger.info("Starting weekly email report", task_id=task_id)
    
    try:
        result = asyncio.run(_send_weekly_email_report_async())
        logger.info("Weekly email report completed", task_id=task_id, **result)
        return result
        
    except Exception as e:
        logger.error("Weekly email report failed", task_id=task_id, error=str(e))
        raise self.retry(countdown=600, exc=e)  # Retry dopo 10 minuti


async def _send_weekly_email_report_async() -> Dict[str, Any]:
    """Implementazione async del report settimanale"""
    from ..services.email_service import get_email_service
    from ..services.database import get_db_session
    from ..models.settings import UserSettings
    from ..models.device import DailyEnergy
    from sqlalchemy import select, and_
    from zoneinfo import ZoneInfo
    
    email_service = get_email_service()
    if not email_service.is_configured:
        return {"success": False, "error": "Email service not configured", "sent": 0}
    
    emails_sent = 0
    errors = []
    
    try:
        italy_tz = ZoneInfo("Europe/Rome")
        today = datetime.now(italy_tz).date()
        week_ago = today - timedelta(days=7)
        
        # Ottieni tutti gli utenti con report settimanale abilitato
        async with get_db_session() as db:
            result = await db.execute(
                select(UserSettings).where(
                    UserSettings.notify_weekly_report == True,
                    UserSettings.notification_email.isnot(None)
                )
            )
            users_with_weekly_report = result.scalars().all()
        
        if not users_with_weekly_report:
            logger.info("No users with weekly report enabled")
            return {"success": True, "sent": 0, "message": "No users with weekly report enabled"}
        
        # Ottieni dati settimanali dal database
        settings = get_settings()
        thing_keys = settings.device_thing_keys
        
        async with get_db_session() as db:
            result = await db.execute(
                select(DailyEnergy).where(
                    and_(
                        DailyEnergy.device_thing_key.in_(thing_keys),
                        DailyEnergy.date >= week_ago,
                        DailyEnergy.date < today
                    )
                ).order_by(DailyEnergy.date)
            )
            daily_records = result.scalars().all()
        
        # Aggrega per giorno
        daily_data = []
        total_production = 0
        total_consumption = 0
        total_self_consumption = 0
        total_from_grid = 0
        total_to_grid = 0
        
        # Raggruppa per data
        from collections import defaultdict
        by_date = defaultdict(lambda: {"production": 0, "consumption": 0, "self_consumption": 0})
        
        for record in daily_records:
            date_str = record.date.strftime("%d/%m")
            by_date[date_str]["production"] += record.energy_generating or 0
            by_date[date_str]["consumption"] += record.energy_consuming or 0
            by_date[date_str]["self_consumption"] += record.energy_autoconsuming or 0
            total_production += record.energy_generating or 0
            total_consumption += record.energy_consuming or 0
            total_self_consumption += record.energy_autoconsuming or 0
            total_from_grid += record.energy_importing or 0
            total_to_grid += record.energy_exporting or 0
        
        # Invia email a ogni utente
        for user_settings in users_with_weekly_report:
            try:
                energy_price = user_settings.energy_price or 0.25
                sell_price = user_settings.sell_price or 0.10
                total_savings = (total_self_consumption * energy_price) + (total_to_grid * sell_price)
                
                # Prepara daily_data con risparmio calcolato per ogni giorno
                daily_data_for_user = []
                for date_str, data in sorted(by_date.items()):
                    day_savings = (data["self_consumption"] * energy_price) + (data.get("to_grid", 0) * sell_price)
                    daily_data_for_user.append({
                        "date": date_str,
                        "production": data["production"],
                        "consumption": data["consumption"],
                        "savings": day_savings
                    })
                
                result = await email_service.send_weekly_report(
                    total_production_kwh=total_production,
                    total_consumption_kwh=total_consumption,
                    total_self_consumption_kwh=total_self_consumption,
                    total_from_grid_kwh=total_from_grid,
                    total_to_grid_kwh=total_to_grid,
                    total_savings_eur=total_savings,
                    daily_data=daily_data_for_user,
                    to_email=user_settings.notification_email,
                    system_name=user_settings.system_name or "Il mio impianto"
                )
                
                if result.get("success"):
                    emails_sent += 1
                else:
                    errors.append(f"User {user_settings.user_id}: {result.get('error')}")
                    
            except Exception as e:
                errors.append(f"User {user_settings.user_id}: {str(e)}")
        
        return {
            "success": True,
            "sent": emails_sent,
            "errors": errors if errors else None,
            "total_production_kwh": total_production
        }
        
    except Exception as e:
        logger.error("Error in weekly email report", error=str(e))
        return {"success": False, "error": str(e), "sent": emails_sent}
