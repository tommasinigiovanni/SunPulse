"""
Device management endpoints - Gestione dispositivi e dati energetici
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from ....services.zcs_api_service import get_zcs_service
from ....services.cache_service import get_cache_service, DataType, make_device_cache_key
from ....services.data_collector import get_task_status, celery_app
from ....models.device import DeviceResponse
from ....config.settings import get_settings

logger = structlog.get_logger()

router = APIRouter()

@router.get("/", response_model=List[DeviceResponse])
async def get_devices():
    """Get all devices"""
    settings = get_settings()
    thing_keys = settings.device_thing_keys
    
    # Generate devices from real configuration
    devices = []
    for i, thing_key in enumerate(thing_keys, 1):
        device = {
            "id": i,
            "thing_key": thing_key,
            "name": f"Dispositivo ZCS {i}",
            "device_type": "inverter",
            "location": f"Installazione {i}",
            "manufacturer": "ZCS Azzurro",
            "model": "ZCS Device",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_seen": datetime.utcnow(),
            "is_active": True
        }
        devices.append(device)
    
    logger.info("Retrieved devices list", count=len(devices), thing_keys=thing_keys)
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: int):
    """Get specific device"""
    settings = get_settings()
    thing_keys = settings.device_thing_keys
    
    # Map device_id to thing_key (1-based indexing)
    if device_id < 1 or device_id > len(thing_keys):
        raise HTTPException(status_code=404, detail="Device not found")
    
    thing_key = thing_keys[device_id - 1]  # Convert to 0-based index
    
    device = {
        "id": device_id,
        "thing_key": thing_key,
        "name": f"Dispositivo ZCS {device_id}",
        "device_type": "inverter",
        "location": f"Installazione {device_id}",
        "manufacturer": "ZCS Azzurro",
        "model": "ZCS Device",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_seen": datetime.utcnow(),
        "is_active": True
    }
    
    logger.info("Retrieved device", device_id=device_id, thing_key=thing_key)
    return device

@router.get("/{device_id}/realtime")
async def get_device_realtime_data(device_id: int):
    """Get latest real-time data for device"""
    # Real thing_key lookup from configuration
    settings = get_settings()
    thing_keys = settings.device_thing_keys
    
    # Map device_id to thing_key (1-based indexing)
    if device_id < 1 or device_id > len(thing_keys):
        raise HTTPException(status_code=404, detail="Device not found")
    
    thing_key = thing_keys[device_id - 1]  # Convert to 0-based index
    
    try:
        cache_service = await get_cache_service()
        zcs_service = await get_zcs_service()
        
        # Prova prima dalla cache
        cache_key = make_device_cache_key(thing_key, DataType.REALTIME)
        cached_data = await cache_service.get(cache_key, DataType.REALTIME)
        
        if cached_data:
            logger.info("Realtime data from cache", device_id=device_id, thing_key=thing_key)
            return {
                "device_id": device_id,
                "thing_key": thing_key,
                "data": cached_data,
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Cache miss - ottieni da ZCS API
        zcs_result = await zcs_service.get_realtime_data([thing_key])
        
        if zcs_result.get('success'):
            device_data = zcs_result['data'].get(thing_key)
            
            if device_data:
                # Cache per future richieste
                await cache_service.set(cache_key, device_data, DataType.REALTIME)
                
                logger.info("Realtime data from ZCS API", device_id=device_id, thing_key=thing_key)
                return {
                    "device_id": device_id,
                    "thing_key": thing_key,
                    "data": device_data,
                    "source": "zcs_api",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        raise HTTPException(status_code=503, detail="Unable to fetch device data")
        
    except Exception as e:
        logger.error("Error fetching realtime data", device_id=device_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{device_id}/historic")
async def get_device_historic_data(
    device_id: int,
    start: Optional[datetime] = Query(None, description="Start timestamp"),
    end: Optional[datetime] = Query(None, description="End timestamp"),
    resolution: str = Query("1h", description="Data resolution (15m, 1h, 1d)")
):
    """Get historical data for device with aggregation"""
    # Real thing_key lookup from configuration
    settings = get_settings()
    thing_keys = settings.device_thing_keys
    
    # Map device_id to thing_key (1-based indexing)
    if device_id < 1 or device_id > len(thing_keys):
        raise HTTPException(status_code=404, detail="Device not found")
    
    thing_key = thing_keys[device_id - 1]  # Convert to 0-based index
    
    # Default time range se non specificato
    if not end:
        end = datetime.utcnow()
    if not start:
        start = end - timedelta(days=7)  # Ultima settimana
    
    try:
        zcs_service = await get_zcs_service()
        cache_service = await get_cache_service()
        
        # Chiave cache per dati storici
        cache_key = make_device_cache_key(
            thing_key, 
            DataType.HISTORIC,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            resolution=resolution
        )
        
        # Prova dalla cache prima
        cached_data = await cache_service.get(cache_key, DataType.HISTORIC)
        
        if cached_data:
            logger.info("Historic data from cache", device_id=device_id, thing_key=thing_key)
            return {
                "device_id": device_id,
                "thing_key": thing_key,
                "data": cached_data,
                "period": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "resolution": resolution
                },
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Cache miss - ottieni da ZCS API
        zcs_result = await zcs_service.get_historic_data([thing_key], start, end, resolution)
        
        if zcs_result.get('success'):
            device_data = zcs_result['data'].get(thing_key)
            
            if device_data:
                # Cache per future richieste
                await cache_service.set(cache_key, device_data, DataType.HISTORIC)
                
                logger.info("Historic data from ZCS API", device_id=device_id, thing_key=thing_key)
                return {
                    "device_id": device_id,
                    "thing_key": thing_key,
                    "data": device_data,
                    "period": {
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                        "resolution": resolution
                    },
                    "source": "zcs_api",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        raise HTTPException(status_code=503, detail="Unable to fetch historic data")
        
    except Exception as e:
        logger.error("Error fetching historic data", device_id=device_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{device_id}/alarms")
async def get_device_alarms(device_id: int):
    """Get current alarm status for device"""
    # Real thing_key lookup from configuration
    settings = get_settings()
    thing_keys = settings.device_thing_keys
    
    # Map device_id to thing_key (1-based indexing)
    if device_id < 1 or device_id > len(thing_keys):
        raise HTTPException(status_code=404, detail="Device not found")
    
    thing_key = thing_keys[device_id - 1]  # Convert to 0-based index
    
    try:
        cache_service = await get_cache_service()
        zcs_service = await get_zcs_service()
        
        # Prova dalla cache
        cache_key = make_device_cache_key(thing_key, DataType.ALARMS)
        cached_data = await cache_service.get(cache_key, DataType.ALARMS)
        
        if cached_data:
            logger.info("Alarm data from cache", device_id=device_id, thing_key=thing_key)
            return {
                "device_id": device_id,
                "thing_key": thing_key,
                "alarms": cached_data,
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Cache miss - ottieni da ZCS API
        zcs_result = await zcs_service.get_device_alarms([thing_key])
        
        if zcs_result.get('success'):
            device_alarms = zcs_result['data'].get(thing_key)
            
            if device_alarms:
                # Cache per future richieste
                await cache_service.set(cache_key, device_alarms, DataType.ALARMS)
                
                logger.info("Alarm data from ZCS API", device_id=device_id, thing_key=thing_key)
                return {
                    "device_id": device_id,
                    "thing_key": thing_key,
                    "alarms": device_alarms,
                    "source": "zcs_api",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Nessun allarme trovato
        return {
            "device_id": device_id,
            "thing_key": thing_key,
            "alarms": [],
            "source": "zcs_api",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error fetching device alarms", device_id=device_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{device_id}/collect")
async def trigger_device_data_collection(device_id: int):
    """Trigger immediate data collection for specific device"""
    try:
        # Avvia task di raccolta dati in background
        task = celery_app.send_task(
            'app.services.data_collector.collect_realtime_data'
        )
        
        logger.info("Triggered data collection", device_id=device_id, task_id=task.id)
        
        return {
            "message": "Data collection triggered",
            "device_id": device_id,
            "task_id": task.id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error triggering data collection", device_id=device_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to trigger collection: {str(e)}")

@router.delete("/{device_id}/cache")
async def clear_device_cache(device_id: int):
    """Clear cache for specific device"""
    # Real thing_key lookup from configuration
    settings = get_settings()
    thing_keys = settings.device_thing_keys
    
    # Map device_id to thing_key (1-based indexing)
    if device_id < 1 or device_id > len(thing_keys):
        raise HTTPException(status_code=404, detail="Device not found")
    
    thing_key = thing_keys[device_id - 1]  # Convert to 0-based index
    
    try:
        cache_service = await get_cache_service()
        
        # Invalida tutte le cache per questo dispositivo
        pattern = f"device:{DataType.REALTIME.value}:{thing_key}*"
        invalidated_count = await cache_service.invalidate_pattern(pattern)
        
        pattern = f"device:{DataType.HISTORIC.value}:{thing_key}*"
        invalidated_count += await cache_service.invalidate_pattern(pattern)
        
        pattern = f"device:{DataType.ALARMS.value}:{thing_key}*"
        invalidated_count += await cache_service.invalidate_pattern(pattern)
        
        logger.info("Device cache cleared", device_id=device_id, thing_key=thing_key, invalidated=invalidated_count)
        
        return {
            "message": "Device cache cleared",
            "device_id": device_id,
            "thing_key": thing_key,
            "invalidated_entries": invalidated_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error clearing device cache", device_id=device_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}") 