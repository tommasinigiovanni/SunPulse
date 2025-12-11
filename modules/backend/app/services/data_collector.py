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
    }
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
    """Task Celery: Raccolta allarmi per tutti i dispositivi attivi"""
    return {"devices_processed": 0, "alarms_found": 0, "errors": 0}

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
