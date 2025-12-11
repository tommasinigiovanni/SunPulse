"""
Data endpoints - Aggregazioni e analisi dati energetici
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

from ....services.zcs_api_service import get_zcs_service
from ....services.cache_service import get_cache_service, DataType, make_cache_key
from ....services.data_collector import get_task_status, celery_app
from ....utils.circuit_breaker import get_all_circuit_breaker_stats

logger = structlog.get_logger()

router = APIRouter()

@router.get("/realtime")
async def get_realtime_data() -> Dict[str, Any]:
    """Ottieni dati in tempo reale aggregati per tutti i dispositivi"""
    try:
        from ....config.settings import get_settings
        
        cache_service = await get_cache_service()
        zcs_service = await get_zcs_service()
        settings = get_settings()
        
        # Real devices from configuration
        thing_keys = settings.device_thing_keys
        
        # Prova dalla cache prima
        cache_key = make_cache_key("system", DataType.REALTIME, aggregated="all")
        cached_data = await cache_service.get(cache_key, DataType.REALTIME)
        
        if cached_data:
            logger.info("System realtime data from cache")
            return {
                "devices": cached_data.get("devices", []),
                "summary": cached_data.get("summary", {}),
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat(),
                "device_count": len(thing_keys)
            }
        
        # Cache miss - ottieni da ZCS API
        zcs_result = await zcs_service.get_realtime_data(thing_keys)
        
        if zcs_result.get('success'):
            # Aggrega i dati per tutti i dispositivi
            devices_array = []
            aggregated_data = {
                "total_power_generating": 0,
                "total_power_consuming": 0,
                "total_power_grid": 0,
                "battery_soc_avg": 0,
                "devices": devices_array,
                "summary": {
                    "active_devices": 0,
                    "total_energy_today": 0,
                    "system_efficiency": 0
                }
            }
            
            active_devices = 0
            device_id = 1
            
            for thing_key, device_data in zcs_result['data'].items():
                if device_data:
                    # Estrai dati reali ZCS e trasforma in formato frontend
                    zcs_device = device_data.get('realtimeData', {}).get('params', {}).get('value', [{}])[0].get(thing_key, {})
                    
                    real_time_device = {
                        "device_id": str(device_id),
                        "thing_key": thing_key,
                        "name": f"Dispositivo ZCS {device_id}",
                        "status": "online",
                        "power": zcs_device.get("powerGenerating", 0),
                        "energy_today": zcs_device.get("energyGenerating", 0),
                        "battery_soc": zcs_device.get("batterySoC", 0),
                        "last_update": zcs_device.get("lastUpdate", datetime.utcnow().isoformat()),
                        "raw_data": device_data
                    }
                    
                    devices_array.append(real_time_device)
                    active_devices += 1
                    device_id += 1
                    
                    # Aggregazione reale dei dati ZCS
                    aggregated_data["total_power_generating"] += real_time_device["power"]
                    aggregated_data["total_power_consuming"] += zcs_device.get("powerConsuming", 0)
                    aggregated_data["summary"]["total_energy_today"] += real_time_device["energy_today"]
                    
                    # Calcola media SOC batteria
                    if real_time_device["battery_soc"] > 0:
                        aggregated_data["battery_soc_avg"] += real_time_device["battery_soc"]
            
            # Finalizza calcoli aggregati
            aggregated_data["summary"]["active_devices"] = active_devices
            aggregated_data["summary"]["total_power"] = aggregated_data["total_power_generating"]
            aggregated_data["summary"]["total_power_consuming"] = aggregated_data["total_power_consuming"]
            
            if active_devices > 0:
                aggregated_data["battery_soc_avg"] = aggregated_data["battery_soc_avg"] / active_devices
                
            # Calcola efficienza sistema
            if aggregated_data["total_power_consuming"] > 0:
                aggregated_data["summary"]["system_efficiency"] = (
                    aggregated_data["total_power_generating"] / 
                    aggregated_data["total_power_consuming"]
                ) * 100
            
            # Cache il risultato aggregato
            await cache_service.set(cache_key, aggregated_data, DataType.REALTIME)
            
            logger.info("System realtime data from ZCS API", active_devices=active_devices)
            return {
                "devices": aggregated_data["devices"],
                "summary": aggregated_data["summary"], 
                "source": "zcs_api",
                "timestamp": datetime.utcnow().isoformat(),
                "device_count": len(thing_keys)
            }
        
        raise HTTPException(status_code=503, detail="Unable to fetch system data")
        
    except Exception as e:
        logger.error("Error fetching system realtime data", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/historical")
async def get_historical_data(
    start: Optional[datetime] = Query(None, description="Start timestamp"),
    end: Optional[datetime] = Query(None, description="End timestamp"),
    resolution: str = Query("1h", description="Data resolution (15m, 1h, 1d)"),
    metric: str = Query("energy", description="Metric type (energy, power, efficiency)")
) -> Dict[str, Any]:
    """Ottieni dati storici aggregati del sistema"""
    
    # Default time range
    if not end:
        end = datetime.utcnow()
    if not start:
        start = end - timedelta(days=7)  # Ultima settimana
    
    try:
        cache_service = await get_cache_service()
        zcs_service = await get_zcs_service()
        
        # Chiave cache per dati storici aggregati
        cache_key = make_cache_key(
            "system",
            DataType.HISTORIC,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            resolution=resolution,
            metric=metric
        )
        
        # Prova dalla cache
        cached_data = await cache_service.get(cache_key, DataType.HISTORIC)
        
        if cached_data:
            logger.info("System historic data from cache", metric=metric, resolution=resolution)
            return {
                "data": cached_data,
                "period": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "resolution": resolution,
                    "metric": metric
                },
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Cache miss - ottieni da ZCS API
        settings = get_settings()
        thing_keys = settings.device_thing_keys
        zcs_result = await zcs_service.get_historic_data(thing_keys, start, end, resolution)
        
        if zcs_result.get('success'):
            # Aggrega dati storici per tutti i dispositivi
            aggregated_historic = {
                "timeline": [],
                "summary": {
                    "total_energy": 0,
                    "peak_power": 0,
                    "avg_efficiency": 0,
                    "data_points": 0
                },
                "devices": {}
            }
            
            for thing_key, device_data in zcs_result['data'].items():
                if device_data:
                    aggregated_historic["devices"][thing_key] = device_data
                    # TODO: Implementare aggregazione reale dei dati storici
            
            # Cache il risultato
            await cache_service.set(cache_key, aggregated_historic, DataType.HISTORIC)
            
            logger.info("System historic data from ZCS API", metric=metric, resolution=resolution)
            return {
                "data": aggregated_historic,
                "period": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "resolution": resolution,
                    "metric": metric
                },
                "source": "zcs_api",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        raise HTTPException(status_code=503, detail="Unable to fetch historic data")
        
    except Exception as e:
        logger.error("Error fetching system historic data", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/summary")
async def get_system_summary() -> Dict[str, Any]:
    """Ottieni riassunto generale del sistema"""
    try:
        cache_service = await get_cache_service()
        
        # Prova dalla cache
        cache_key = make_cache_key("system", DataType.AGGREGATED, summary="daily")
        cached_data = await cache_service.get(cache_key, DataType.AGGREGATED)
        
        if cached_data:
            logger.info("System summary from cache")
            return {
                "summary": cached_data,
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Calcola summary aggregato
        # TODO: Implementare calcolo reale da InfluxDB
        system_summary = {
            "energy_today": 25.4,  # kWh
            "energy_month": 645.8,  # kWh
            "energy_year": 7234.2,  # kWh
            "peak_power_today": 3.2,  # kW
            "current_power": 1.8,  # kW
            "system_efficiency": 92.5,  # %
            "co2_saved_kg": 3617.1,  # kg CO2
            "money_saved_eur": 1447.25,  # EUR
            "devices": {
                "total": 2,
                "active": 2,
                "maintenance": 0,
                "error": 0
            },
            "alarms": {
                "active": 0,
                "total_today": 2,
                "critical": 0
            },
            "performance": {
                "uptime_percent": 99.2,
                "data_collection_rate": 98.8,
                "api_response_time_ms": 245
            }
        }
        
        # Cache per 5 minuti
        await cache_service.set(cache_key, system_summary, DataType.AGGREGATED, ttl_seconds=300)
        
        logger.info("System summary calculated")
        return {
            "summary": system_summary,
            "source": "calculated",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error calculating system summary", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/monitoring")
async def get_system_monitoring() -> Dict[str, Any]:
    """Ottieni stato monitoring e health del sistema"""
    try:
        cache_service = await get_cache_service()
        
        # Statistiche cache
        cache_stats = cache_service.get_stats()
        
        # Statistiche circuit breaker
        circuit_stats = get_all_circuit_breaker_stats()
        
        # Task attivi Celery
        inspect = celery_app.control.inspect()
        active_tasks_raw = inspect.active()
        active_tasks = []
        if active_tasks_raw:
            for worker_name, tasks in active_tasks_raw.items():
                for task in tasks:
                    active_tasks.append({
                        "task_id": task.get('id'),
                        "name": task.get('name'),
                        "worker": worker_name
                    })
        
        # Health check ZCS API
        zcs_service = await get_zcs_service()
        zcs_health = await zcs_service.health_check()
        
        monitoring_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": {
                "overall_status": "healthy",  # healthy, warning, error
                "uptime_hours": 72.5,
                "last_restart": "2024-01-15T10:30:00Z"
            },
            "services": {
                "zcs_api": {
                    "status": "healthy" if zcs_health.get("healthy") else "error",
                    "response_time_ms": zcs_health.get("response_time_ms", 0),
                    "circuit_breaker_state": zcs_health.get("circuit_breaker_state", "unknown")
                },
                "cache": {
                    "status": "healthy" if cache_stats["redis_connected"] else "error",
                    "hit_rate_percent": cache_stats["hit_rate_percent"],
                    "total_requests": cache_stats["total_requests"],
                    "memory_usage": cache_stats["memory_cache_size"]
                },
                "data_collection": {
                    "status": "healthy",
                    "active_tasks": len(active_tasks),
                    "last_collection": "2024-01-15T14:28:00Z",
                    "success_rate_percent": 98.5
                }
            },
            "circuit_breakers": circuit_stats,
            "performance": {
                "avg_api_response_ms": 234,
                "data_points_per_minute": 120,
                "cache_hit_rate": cache_stats["hit_rate_percent"],
                "error_rate_percent": 0.2
            },
            "active_tasks": active_tasks,
            "alerts": [
                # TODO: Implementare sistema di alert
            ]
        }
        
        # Determina stato generale
        if not zcs_health.get("healthy") or not cache_stats["redis_connected"]:
            monitoring_data["system_health"]["overall_status"] = "error"
        elif cache_stats["hit_rate_percent"] < 70:
            monitoring_data["system_health"]["overall_status"] = "warning"
        
        logger.info("System monitoring data generated")
        return monitoring_data
        
    except Exception as e:
        logger.error("Error generating monitoring data", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/collection/trigger")
async def trigger_data_collection() -> Dict[str, Any]:
    """Avvia raccolta dati manuale per tutti i dispositivi"""
    try:
        # Avvia task di raccolta dati realtime
        realtime_task = celery_app.send_task(
            'app.services.data_collector.collect_realtime_data'
        )
        
        # Avvia task raccolta allarmi
        alarm_task = celery_app.send_task(
            'app.services.data_collector.collect_alarm_data'
        )
        
        logger.info("Triggered manual data collection", 
                   realtime_task_id=realtime_task.id,
                   alarm_task_id=alarm_task.id)
        
        return {
            "message": "Data collection triggered",
            "tasks": {
                "realtime": {
                    "task_id": realtime_task.id,
                    "status": "pending"
                },
                "alarms": {
                    "task_id": alarm_task.id,
                    "status": "pending"
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error triggering data collection", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to trigger collection: {str(e)}")

@router.get("/collection/status")
async def get_collection_status() -> Dict[str, Any]:
    """Ottieni stato delle attività di raccolta dati"""
    try:
        # Task attivi
        inspect = celery_app.control.inspect()
        active_tasks_raw = inspect.active()
        active_tasks = []
        if active_tasks_raw:
            for worker_name, tasks in active_tasks_raw.items():
                for task in tasks:
                    active_tasks.append({
                        "task_id": task.get('id'),
                        "name": task.get('name'),
                        "worker": worker_name
                    })
        
        # Filtra per task di data collection
        collection_tasks = [
            task for task in active_tasks 
            if 'collect' in task.get('name', '')
        ]
        
        # Statistiche ultime 24h (mock data)
        collection_stats = {
            "last_24h": {
                "realtime_collections": 720,  # ogni 2 min = 720/day
                "alarm_collections": 2880,    # ogni 30 sec = 2880/day
                "historic_collections": 1,    # una volta al giorno
                "success_rate_percent": 98.5,
                "avg_duration_seconds": 4.2,
                "total_data_points": 86400
            },
            "current": {
                "active_tasks": len(collection_tasks),
                "queue_size": 0,
                "last_success": "2024-01-15T14:28:00Z",
                "next_scheduled": "2024-01-15T14:30:00Z"
            }
        }
        
        return {
            "status": collection_stats,
            "active_tasks": collection_tasks,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting collection status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/cache")
async def clear_system_cache() -> Dict[str, Any]:
    """Pulisci tutta la cache del sistema"""
    try:
        cache_service = await get_cache_service()
        
        # Statistiche pre-clear
        stats_before = cache_service.get_stats()
        
        # Pulisci tutta la cache
        success = await cache_service.clear_all()
        
        if success:
            logger.info("System cache cleared", entries_before=stats_before["total_requests"])
            return {
                "message": "System cache cleared successfully",
                "stats_before": stats_before,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
            
    except Exception as e:
        logger.error("Error clearing system cache", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}") 