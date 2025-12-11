"""
Alarm endpoints - Gestione allarmi dispositivi e sistema
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from ....services.zcs_api_service import get_zcs_service
from ....services.cache_service import get_cache_service, DataType, make_cache_key, make_device_cache_key
from ....models.device import AlarmResponse, AlarmLevel, AlarmCategory

logger = structlog.get_logger()

router = APIRouter()

@router.get("/", response_model=List[AlarmResponse])
async def get_system_alarms(
    active_only: bool = Query(True, description="Show only active alarms"),
    level: Optional[AlarmLevel] = Query(None, description="Filter by alarm level"),
    limit: int = Query(100, description="Max number of alarms to return")
) -> List[AlarmResponse]:
    """Ottieni tutti gli allarmi del sistema"""
    try:
        cache_service = await get_cache_service()
        zcs_service = await get_zcs_service()
        
        # Chiave cache per allarmi di sistema
        cache_key = make_cache_key(
            "system", 
            DataType.ALARMS,
            active_only=str(active_only),
            level=level.value if level else "all",
            limit=str(limit)
        )
        
        # Prova dalla cache prima
        cached_alarms = await cache_service.get(cache_key, DataType.ALARMS)
        
        if cached_alarms:
            logger.info("System alarms from cache", count=len(cached_alarms))
            return cached_alarms
        
        # Cache miss - ottieni da ZCS API
        from ....config.settings import get_settings
        settings = get_settings()
        thing_keys = settings.device_thing_keys  # Real devices from configuration
        zcs_result = await zcs_service.get_device_alarms(thing_keys)
        
        if zcs_result.get('success'):
            all_alarms = []
            
            for thing_key, device_alarms in zcs_result['data'].items():
                if device_alarms:
                    # Converte allarmi ZCS nel formato standardizzato
                    for alarm_data in device_alarms:
                        alarm = AlarmResponse(
                            id=alarm_data.get('id', f"{thing_key}_{alarm_data.get('code', 'unknown')}"),
                            device_thing_key=thing_key,
                            device_name=f"Device {thing_key}",
                            code=alarm_data.get('code', 'UNKNOWN'),
                            message=alarm_data.get('message', 'Unknown alarm'),
                            level=AlarmLevel(alarm_data.get('severity', 'warning')),
                            category=AlarmCategory(alarm_data.get('category', 'system')),
                            active=alarm_data.get('active', True),
                            acknowledged=alarm_data.get('acknowledged', False),
                            triggered_at=datetime.fromisoformat(alarm_data.get('timestamp', datetime.utcnow().isoformat())),
                            description=alarm_data.get('description'),
                            suggested_action=alarm_data.get('action')
                        )
                        
                        # Filtra per stato attivo se richiesto
                        if not active_only or alarm.active:
                            # Filtra per livello se specificato
                            if not level or alarm.level == level:
                                all_alarms.append(alarm)
            
            # Ordina per timestamp (più recenti per primi) e limita
            all_alarms.sort(key=lambda x: x.triggered_at, reverse=True)
            limited_alarms = all_alarms[:limit]
            
            # Cache il risultato
            await cache_service.set(cache_key, limited_alarms, DataType.ALARMS)
            
            logger.info("System alarms from ZCS API", count=len(limited_alarms))
            return limited_alarms
        
        # Nessun dato disponibile - ritorna lista vuota
        logger.warning("No alarm data available from ZCS API")
        return []
        
    except Exception as e:
        logger.error("Error fetching system alarms", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/device/{device_id}", response_model=List[AlarmResponse])
async def get_device_alarms(
    device_id: int,
    active_only: bool = Query(True, description="Show only active alarms"),
    limit: int = Query(50, description="Max number of alarms to return")
) -> List[AlarmResponse]:
    """Ottieni allarmi specifici per un dispositivo"""
    # Mock thing_key lookup
    thing_key_map = {1: "device_001", 2: "device_002"}
    thing_key = thing_key_map.get(device_id)
    
    if not thing_key:
        raise HTTPException(status_code=404, detail="Device not found")
    
    try:
        cache_service = await get_cache_service()
        zcs_service = await get_zcs_service()
        
        # Chiave cache per allarmi dispositivo
        cache_key = make_device_cache_key(
            thing_key,
            DataType.ALARMS,
            active_only=str(active_only),
            limit=str(limit)
        )
        
        # Prova dalla cache prima
        cached_alarms = await cache_service.get(cache_key, DataType.ALARMS)
        
        if cached_alarms:
            logger.info("Device alarms from cache", device_id=device_id, thing_key=thing_key, count=len(cached_alarms))
            return cached_alarms
        
        # Cache miss - ottieni da ZCS API
        zcs_result = await zcs_service.get_device_alarms([thing_key])
        
        if zcs_result.get('success'):
            device_alarms = zcs_result['data'].get(thing_key, [])
            processed_alarms = []
            
            for alarm_data in device_alarms:
                alarm = AlarmResponse(
                    id=alarm_data.get('id', f"{thing_key}_{alarm_data.get('code', 'unknown')}"),
                    device_thing_key=thing_key,
                    device_name=f"Device {thing_key}",
                    code=alarm_data.get('code', 'UNKNOWN'),
                    message=alarm_data.get('message', 'Unknown alarm'),
                    level=AlarmLevel(alarm_data.get('severity', 'warning')),
                    category=AlarmCategory(alarm_data.get('category', 'system')),
                    active=alarm_data.get('active', True),
                    acknowledged=alarm_data.get('acknowledged', False),
                    triggered_at=datetime.fromisoformat(alarm_data.get('timestamp', datetime.utcnow().isoformat())),
                    description=alarm_data.get('description'),
                    suggested_action=alarm_data.get('action')
                )
                
                # Filtra per stato attivo se richiesto
                if not active_only or alarm.active:
                    processed_alarms.append(alarm)
            
            # Ordina per timestamp e limita
            processed_alarms.sort(key=lambda x: x.triggered_at, reverse=True)
            limited_alarms = processed_alarms[:limit]
            
            # Cache il risultato
            await cache_service.set(cache_key, limited_alarms, DataType.ALARMS)
            
            logger.info("Device alarms from ZCS API", device_id=device_id, thing_key=thing_key, count=len(limited_alarms))
            return limited_alarms
        
        # Nessun dato disponibile
        logger.warning("No alarm data available for device", device_id=device_id, thing_key=thing_key)
        return []
        
    except Exception as e:
        logger.error("Error fetching device alarms", device_id=device_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/historic")
async def get_historic_alarms(
    start: Optional[datetime] = Query(None, description="Start timestamp"),
    end: Optional[datetime] = Query(None, description="End timestamp"),
    level: Optional[AlarmLevel] = Query(None, description="Filter by alarm level"),
    category: Optional[AlarmCategory] = Query(None, description="Filter by alarm category"),
    limit: int = Query(200, description="Max number of alarms to return")
) -> Dict[str, Any]:
    """Ottieni storico allarmi con filtri avanzati"""
    # Default time range
    if not end:
        end = datetime.utcnow()
    if not start:
        start = end - timedelta(days=30)  # Ultimo mese
    
    try:
        cache_service = await get_cache_service()
        zcs_service = await get_zcs_service()
        
        # Chiave cache per allarmi storici
        cache_key = make_cache_key(
            "system",
            DataType.ALARMS,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            level=level.value if level else "all",
            category=category.value if category else "all",
            limit=str(limit),
            historic="true"
        )
        
        # Prova dalla cache prima
        cached_data = await cache_service.get(cache_key, DataType.ALARMS)
        
        if cached_data:
            logger.info("Historic alarms from cache")
            return {
                "alarms": cached_data["alarms"],
                "summary": cached_data["summary"],
                "period": {
                    "start": start.isoformat(),
                    "end": end.isoformat()
                },
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Cache miss - ottieni da ZCS API
        settings = get_settings()
        thing_keys = settings.device_thing_keys
        zcs_result = await zcs_service.get_historic_alarms(thing_keys, start, end)
        
        if zcs_result.get('success'):
            all_historic_alarms = []
            summary = {
                "total_alarms": 0,
                "by_level": {"critical": 0, "warning": 0, "info": 0},
                "by_category": {"system": 0, "battery": 0, "inverter": 0, "communication": 0},
                "most_frequent": []
            }
            
            for thing_key, historic_alarms in zcs_result['data'].items():
                if historic_alarms:
                    for alarm_data in historic_alarms:
                        # Filtra per data se nei parametri ZCS
                        alarm_timestamp = datetime.fromisoformat(alarm_data.get('timestamp', start.isoformat()))
                        if start <= alarm_timestamp <= end:
                            alarm = AlarmResponse(
                                id=alarm_data.get('id', f"{thing_key}_{alarm_data.get('code', 'unknown')}"),
                                device_thing_key=thing_key,
                                device_name=f"Device {thing_key}",
                                code=alarm_data.get('code', 'UNKNOWN'),
                                message=alarm_data.get('message', 'Unknown alarm'),
                                level=AlarmLevel(alarm_data.get('severity', 'warning')),
                                category=AlarmCategory(alarm_data.get('category', 'system')),
                                active=alarm_data.get('active', False),  # Historic sono di solito resolved
                                acknowledged=alarm_data.get('acknowledged', True),
                                triggered_at=alarm_timestamp,
                                resolved_at=datetime.fromisoformat(alarm_data.get('resolved_at')) if alarm_data.get('resolved_at') else None,
                                description=alarm_data.get('description'),
                                suggested_action=alarm_data.get('action')
                            )
                            
                            # Applica filtri
                            if level and alarm.level != level:
                                continue
                            if category and alarm.category != category:
                                continue
                            
                            all_historic_alarms.append(alarm)
                            
                            # Aggiorna summary
                            summary["total_alarms"] += 1
                            summary["by_level"][alarm.level.value] += 1
                            summary["by_category"][alarm.category.value] += 1
            
            # Ordina e limita
            all_historic_alarms.sort(key=lambda x: x.triggered_at, reverse=True)
            limited_alarms = all_historic_alarms[:limit]
            
            # Calcola allarmi più frequenti
            alarm_codes = {}
            for alarm in all_historic_alarms:
                code = alarm.code
                if code not in alarm_codes:
                    alarm_codes[code] = {"code": code, "count": 0, "last_occurred": alarm.triggered_at}
                alarm_codes[code]["count"] += 1
                if alarm.triggered_at > alarm_codes[code]["last_occurred"]:
                    alarm_codes[code]["last_occurred"] = alarm.triggered_at
            
            summary["most_frequent"] = sorted(
                alarm_codes.values(),
                key=lambda x: x["count"],
                reverse=True
            )[:5]
            
            result_data = {
                "alarms": limited_alarms,
                "summary": summary
            }
            
            # Cache il risultato
            await cache_service.set(cache_key, result_data, DataType.ALARMS)
            
            logger.info("Historic alarms from ZCS API", total=summary["total_alarms"], returned=len(limited_alarms))
            return {
                "alarms": limited_alarms,
                "summary": summary,
                "period": {
                    "start": start.isoformat(),
                    "end": end.isoformat()
                },
                "source": "zcs_api",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Nessun dato disponibile
        logger.warning("No historic alarm data available")
        return {
            "alarms": [],
            "summary": {
                "total_alarms": 0,
                "by_level": {"critical": 0, "warning": 0, "info": 0},
                "by_category": {"system": 0, "battery": 0, "inverter": 0, "communication": 0},
                "most_frequent": []
            },
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat()
            },
            "source": "zcs_api",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error fetching historic alarms", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/summary")
async def get_alarm_summary() -> Dict[str, Any]:
    """Ottieni riassunto allarmi attivi del sistema"""
    try:
        cache_service = await get_cache_service()
        
        # Chiave cache per summary allarmi
        cache_key = make_cache_key("system", DataType.ALARMS, summary="active")
        
        # Prova dalla cache prima
        cached_summary = await cache_service.get(cache_key, DataType.ALARMS)
        
        if cached_summary:
            logger.info("Alarm summary from cache")
            return {
                "summary": cached_summary,
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Cache miss - calcola da API
        system_alarms = await get_system_alarms(active_only=True, limit=1000)
        
        summary = {
            "total_active": len(system_alarms),
            "by_level": {"critical": 0, "warning": 0, "info": 0},
            "by_category": {"system": 0, "battery": 0, "inverter": 0, "communication": 0},
            "by_device": {},
            "unacknowledged": 0,
            "oldest_active": None,
            "newest_active": None
        }
        
        if system_alarms:
            # Calcola statistiche
            timestamps = []
            for alarm in system_alarms:
                summary["by_level"][alarm.level.value] += 1
                summary["by_category"][alarm.category.value] += 1
                
                device_key = alarm.device_thing_key
                if device_key not in summary["by_device"]:
                    summary["by_device"][device_key] = 0
                summary["by_device"][device_key] += 1
                
                if not alarm.acknowledged:
                    summary["unacknowledged"] += 1
                
                timestamps.append(alarm.triggered_at)
            
            # Trova oldest e newest
            if timestamps:
                summary["oldest_active"] = min(timestamps).isoformat()
                summary["newest_active"] = max(timestamps).isoformat()
        
        # Cache per 1 minuto (dati dinamici)
        await cache_service.set(cache_key, summary, DataType.ALARMS)
        
        logger.info("Alarm summary calculated", total_active=summary["total_active"])
        return {
            "summary": summary,
            "source": "calculated",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error generating alarm summary", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{alarm_id}/acknowledge")
async def acknowledge_alarm(alarm_id: str) -> Dict[str, Any]:
    """Conferma (acknowledge) un allarme specifico"""
    try:
        # TODO: Implementare acknowledge nel database e/o ZCS API
        # Per ora simuliamo l'operazione
        
        logger.info("Alarm acknowledged", alarm_id=alarm_id)
        
        # Invalida cache allarmi per aggiornamento
        cache_service = await get_cache_service()
        await cache_service.delete_pattern("alarms:*")
        
        return {
            "alarm_id": alarm_id,
            "acknowledged": True,
            "acknowledged_at": datetime.utcnow().isoformat(),
            "acknowledged_by": "system"  # TODO: User authentication
        }
        
    except Exception as e:
        logger.error("Error acknowledging alarm", alarm_id=alarm_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/cache")
async def clear_alarm_cache() -> Dict[str, Any]:
    """Pulisci cache allarmi (admin endpoint)"""
    try:
        cache_service = await get_cache_service()
        deleted_count = await cache_service.delete_pattern("alarms:*")
        
        logger.info("Alarm cache cleared", deleted_keys=deleted_count)
        return {
            "message": "Alarm cache cleared successfully",
            "deleted_keys": deleted_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error clearing alarm cache", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 