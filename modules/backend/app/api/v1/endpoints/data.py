"""
Data endpoints - Aggregazioni e analisi dati energetici
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

from ....config.settings import get_settings
from ....services.zcs_api_service import get_zcs_service
from ....services.cache_service import get_cache_service, DataType, make_cache_key
from ....services.data_collector import get_task_status, celery_app
from ....utils.circuit_breaker import get_all_circuit_breaker_stats

logger = structlog.get_logger()

router = APIRouter()

async def get_daily_energy_from_historical(zcs_service, thing_keys: List[str]) -> Dict[str, float]:
    """Calcola energia giornaliera dalla differenza dei valori cumulativi storici"""
    try:
        # Prendi dati da mezzanotte a ora
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        hist_result = await zcs_service.get_historic_data(thing_keys, start_of_day, now, "15m")
        
        if not hist_result.get('success'):
            return {}
        
        daily_energy = {
            "energy_generating": 0,
            "energy_consuming": 0,
            "energy_autoconsuming": 0,
            "energy_importing": 0,
            "energy_exporting": 0,
            "energy_charging": 0,
            "energy_discharging": 0,
        }
        
        for thing_key, device_data in hist_result['data'].items():
            if not device_data:
                continue
                
            hist = device_data.get('historicData', {}).get('params', {}).get('value', [])
            if not hist or len(hist) == 0:
                continue
                
            zcs = hist[0].get(thing_key, {})
            
            # Mappa campi: nome ZCS -> nome interno
            field_mapping = {
                "energyGeneratingTotalDecimal": "energy_generating",
                "energyConsumingTotalDecimal": "energy_consuming",
                "energyAutoconsumingTotalDecimal": "energy_autoconsuming",
                "energyImportingTotalDecimal": "energy_importing",
                "energyExportingTotalDecimal": "energy_exporting",
                "energyChargingTotalDecimal": "energy_charging",
                "energyDischargingTotalDecimal": "energy_discharging",
            }
            
            for zcs_field, internal_field in field_mapping.items():
                vals = zcs.get(zcs_field, [])
                if isinstance(vals, list) and len(vals) >= 2:
                    first = vals[0] if vals[0] else 0
                    last = vals[-1] if vals[-1] else 0
                    diff = max(0, last - first)  # Energia non può essere negativa
                    daily_energy[internal_field] += diff
        
        logger.debug("Daily energy calculated from historical", daily_energy=daily_energy)
        return daily_energy
        
    except Exception as e:
        logger.warning("Failed to get daily energy from historical", error=str(e))
        return {}


@router.get("/realtime")
async def get_realtime_data() -> Dict[str, Any]:
    """Ottieni dati in tempo reale aggregati per tutti i dispositivi"""
    try:
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
        
        # Ottieni energia giornaliera da dati storici (più affidabile)
        daily_energy = await get_daily_energy_from_historical(zcs_service, thing_keys)
        
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
                    
                    # Dati energetici giornalieri: usa direttamente i campi energy* dall'API realtime
                    # Questi sono i valori giornalieri già calcolati da ZCS (si resettano a mezzanotte)
                    # Fallback ai dati storici solo se i campi realtime sono vuoti
                    device_daily = {
                        "energy_generating": zcs_device.get("energyGenerating", 0) or daily_energy.get("energy_generating", 0),
                        "energy_consuming": zcs_device.get("energyConsuming", 0) or daily_energy.get("energy_consuming", 0),
                        "energy_autoconsuming": zcs_device.get("energyAutoconsuming", 0) or daily_energy.get("energy_autoconsuming", 0),
                        "energy_from_grid": zcs_device.get("energyImporting", 0) or daily_energy.get("energy_importing", 0),
                        "energy_to_grid": zcs_device.get("energyExporting", 0) or daily_energy.get("energy_exporting", 0),
                        "energy_to_battery": zcs_device.get("energyCharging", 0) or daily_energy.get("energy_charging", 0),
                        "energy_from_battery": zcs_device.get("energyDischarging", 0) or daily_energy.get("energy_discharging", 0),
                    }
                    
                    logger.debug("Device daily energy", thing_key=thing_key, daily=device_daily, 
                                zcs_generating=zcs_device.get("energyGenerating"),
                                zcs_consuming=zcs_device.get("energyConsuming"))
                    
                    real_time_device = {
                        "device_id": str(device_id),
                        "thing_key": thing_key,
                        "name": f"Inverter ZCS {device_id}",
                        "status": "online",
                        "power": zcs_device.get("powerGenerating", 0),
                        "power_consuming": zcs_device.get("powerConsuming", 0),
                        "energy_today": device_daily["energy_generating"],  # Usa dato storico
                        "energy_consumed_today": device_daily["energy_consuming"],
                        "battery_soc": zcs_device.get("batterySoC", 0),
                        "last_update": zcs_device.get("lastUpdate", datetime.utcnow().isoformat()),
                        "daily_energy": device_daily,  # Tutti i dati giornalieri
                        "raw_data": device_data
                    }
                    
                    devices_array.append(real_time_device)
                    active_devices += 1
                    device_id += 1
                    
                    # Aggregazione reale dei dati ZCS
                    aggregated_data["total_power_generating"] += real_time_device["power"]
                    aggregated_data["total_power_consuming"] += zcs_device.get("powerConsuming", 0)
                    
                    # Calcola media SOC batteria
                    if real_time_device["battery_soc"] > 0:
                        aggregated_data["battery_soc_avg"] += real_time_device["battery_soc"]
            
            # Finalizza calcoli aggregati
            aggregated_data["summary"]["active_devices"] = active_devices
            aggregated_data["summary"]["online_devices"] = active_devices  # Alias per frontend
            aggregated_data["summary"]["total_devices"] = len(thing_keys)  # Totale dispositivi configurati
            aggregated_data["summary"]["total_power"] = aggregated_data["total_power_generating"]
            aggregated_data["summary"]["total_power_consuming"] = aggregated_data["total_power_consuming"]
            
            if active_devices > 0:
                aggregated_data["battery_soc_avg"] = aggregated_data["battery_soc_avg"] / active_devices
            
            # Aggrega dati energetici giornalieri da tutti i dispositivi
            # Usa i valori energy* dall'API realtime (già giornalieri, si resettano a mezzanotte)
            total_energy_generating = 0
            total_energy_consuming = 0
            total_energy_autoconsuming = 0
            total_energy_from_grid = 0
            total_energy_to_grid = 0
            total_energy_to_battery = 0
            total_energy_from_battery = 0
            
            for dev in devices_array:
                dev_daily = dev.get("daily_energy", {})
                total_energy_generating += dev_daily.get("energy_generating", 0)
                total_energy_consuming += dev_daily.get("energy_consuming", 0)
                total_energy_autoconsuming += dev_daily.get("energy_autoconsuming", 0)
                total_energy_from_grid += dev_daily.get("energy_from_grid", 0)
                total_energy_to_grid += dev_daily.get("energy_to_grid", 0)
                total_energy_to_battery += dev_daily.get("energy_to_battery", 0)
                total_energy_from_battery += dev_daily.get("energy_from_battery", 0)
            
            # Calcola consumo totale come somma dei componenti (più accurato)
            # Consumo = Autoconsumo + Dalla Rete + Dalla Batteria
            energy_consumed_calculated = total_energy_autoconsuming + total_energy_from_grid + total_energy_from_battery
            
            # Se il calcolo dà 0 ma abbiamo un valore consumo totale, usa quello
            if energy_consumed_calculated == 0 and total_energy_consuming > 0:
                energy_consumed_calculated = total_energy_consuming
            
            aggregated_data["summary"]["total_energy_today"] = total_energy_generating
            aggregated_data["summary"]["energy_consumed_today"] = energy_consumed_calculated
            aggregated_data["summary"]["energy_autoconsuming_today"] = total_energy_autoconsuming
            aggregated_data["summary"]["energy_from_grid_today"] = total_energy_from_grid
            aggregated_data["summary"]["energy_to_grid_today"] = total_energy_to_grid
            aggregated_data["summary"]["energy_to_battery_today"] = total_energy_to_battery
            aggregated_data["summary"]["energy_from_battery_today"] = total_energy_from_battery
            aggregated_data["summary"]["energy_self_consumed_today"] = total_energy_autoconsuming
            
            logger.info("Daily energy summary calculated", 
                       generating=total_energy_generating,
                       consuming=energy_consumed_calculated,
                       autoconsuming=total_energy_autoconsuming)
            
            # Calcolo bilancio energetico
            production = aggregated_data["total_power_generating"]
            consumption = aggregated_data["total_power_consuming"]
            
            # Autoconsumo = energia prodotta usata direttamente (min tra produzione e consumo)
            self_consumption = min(production, consumption)
            
            # Dalla rete = consumo - autoconsumo (quando consumo > produzione)
            from_grid = max(0, consumption - production)
            
            # Immissione in rete = produzione - autoconsumo (quando produzione > consumo)
            to_grid = max(0, production - consumption)
            
            # Aggiungi al summary (dati istantanei in W)
            aggregated_data["summary"]["self_consumption"] = self_consumption  # Autoconsumo in W
            aggregated_data["summary"]["from_grid"] = from_grid  # Prelievo dalla rete in W
            aggregated_data["summary"]["to_grid"] = to_grid  # Immissione in rete in W
            aggregated_data["summary"]["battery_soc"] = aggregated_data["battery_soc_avg"]  # SOC batteria %
                
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
            
            # Estrai e aggrega timeline da tutti i dispositivi
            timeline_dict = {}  # timestamp -> {production, consumption}
            
            for thing_key, device_data in zcs_result['data'].items():
                if device_data:
                    aggregated_historic["devices"][thing_key] = device_data
                    
                    # Estrai dati storici dal formato ZCS
                    hist_data = device_data.get('historicData', {}).get('params', {}).get('value', [])
                    if hist_data and len(hist_data) > 0:
                        zcs_values = hist_data[0].get(thing_key, {})
                        
                        # Array di valori per power
                        power_gen = zcs_values.get('powerGenerating', [])
                        power_cons = zcs_values.get('powerConsuming', [])
                        
                        # Calcola numero di punti e genera timestamp
                        num_points = max(len(power_gen) if isinstance(power_gen, list) else 0,
                                        len(power_cons) if isinstance(power_cons, list) else 0)
                        
                        if num_points > 0:
                            # Calcola intervallo in base alla risoluzione
                            total_seconds = (end - start).total_seconds()
                            interval_seconds = total_seconds / num_points if num_points > 1 else 3600
                            
                            for i in range(num_points):
                                ts = start + timedelta(seconds=interval_seconds * i)
                                ts_str = ts.isoformat()
                                
                                if ts_str not in timeline_dict:
                                    timeline_dict[ts_str] = {"production": 0, "consumption": 0}
                                
                                # Aggiungi valori (gestendo None e tipi diversi)
                                if isinstance(power_gen, list) and i < len(power_gen):
                                    val = power_gen[i]
                                    timeline_dict[ts_str]["production"] += val if val else 0
                                
                                if isinstance(power_cons, list) and i < len(power_cons):
                                    val = power_cons[i]
                                    timeline_dict[ts_str]["consumption"] += val if val else 0
            
            # Converti dict in lista ordinata per timestamp
            for ts_str in sorted(timeline_dict.keys()):
                values = timeline_dict[ts_str]
                aggregated_historic["timeline"].append({
                    "timestamp": ts_str,
                    "production": values["production"],
                    "consumption": values["consumption"]
                })
                
                # Aggiorna summary
                aggregated_historic["summary"]["data_points"] += 1
                if values["production"] > aggregated_historic["summary"]["peak_power"]:
                    aggregated_historic["summary"]["peak_power"] = values["production"]
            
            logger.info("Historical timeline generated", 
                       points=len(aggregated_historic["timeline"]),
                       devices=len(aggregated_historic["devices"]))
            
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

@router.get("/daily-energy")
async def get_daily_energy_history(
    days: int = Query(30, description="Number of days of history", ge=1, le=365)
) -> Dict[str, Any]:
    """Ottieni storico energia giornaliera (produzione/consumo in kWh per giorno)"""
    try:
        zcs_service = await get_zcs_service()
        settings = get_settings()
        thing_keys = settings.device_thing_keys
        
        daily_data = []
        now = datetime.utcnow()
        
        # Per ogni giorno, ottieni i dati di energia
        # L'API ZCS ha campi energy* che si resettano a mezzanotte
        # Quindi dobbiamo fare una richiesta per ogni giorno e prendere l'ultimo valore
        
        for day_offset in range(days - 1, -1, -1):
            target_date = now - timedelta(days=day_offset)
            day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Se è oggi, usa l'ora corrente come fine
            if day_offset == 0:
                day_end = now
            
            try:
                # Ottieni dati storici per questo giorno
                hist_result = await zcs_service.get_historic_data(thing_keys, day_start, day_end, "1h")
                
                daily_production = 0
                daily_consumption = 0
                
                if hist_result.get('success'):
                    for thing_key, device_data in hist_result['data'].items():
                        if device_data:
                            hist = device_data.get('historicData', {}).get('params', {}).get('value', [])
                            if hist and len(hist) > 0:
                                zcs = hist[0].get(thing_key, {})
                                
                                # Prova i campi energy*TotalDecimal (cumulativi)
                                energy_gen_vals = zcs.get('energyGeneratingTotalDecimal', [])
                                energy_cons_vals = zcs.get('energyConsumingTotalDecimal', [])
                                
                                # Se non esistono, prova energyGenerating/energyConsuming
                                if not energy_gen_vals or not isinstance(energy_gen_vals, list):
                                    energy_gen_vals = zcs.get('energyGenerating', [])
                                if not energy_cons_vals or not isinstance(energy_cons_vals, list):
                                    energy_cons_vals = zcs.get('energyConsuming', [])
                                
                                # Calcola differenza tra primo e ultimo valore (energia del giorno)
                                if isinstance(energy_gen_vals, list) and len(energy_gen_vals) >= 2:
                                    first = energy_gen_vals[0] if energy_gen_vals[0] else 0
                                    last = energy_gen_vals[-1] if energy_gen_vals[-1] else 0
                                    daily_production += max(0, last - first)
                                elif isinstance(energy_gen_vals, list) and len(energy_gen_vals) == 1:
                                    daily_production += energy_gen_vals[0] if energy_gen_vals[0] else 0
                                
                                if isinstance(energy_cons_vals, list) and len(energy_cons_vals) >= 2:
                                    first = energy_cons_vals[0] if energy_cons_vals[0] else 0
                                    last = energy_cons_vals[-1] if energy_cons_vals[-1] else 0
                                    daily_consumption += max(0, last - first)
                                elif isinstance(energy_cons_vals, list) and len(energy_cons_vals) == 1:
                                    daily_consumption += energy_cons_vals[0] if energy_cons_vals[0] else 0
                
                daily_data.append({
                    "date": target_date.strftime("%Y-%m-%d"),
                    "date_label": target_date.strftime("%d/%m"),
                    "production_kwh": round(daily_production, 2),
                    "consumption_kwh": round(daily_consumption, 2)
                })
                
            except Exception as e:
                logger.warning(f"Failed to get data for {target_date.date()}", error=str(e))
                # Aggiungi placeholder per questo giorno
                daily_data.append({
                    "date": target_date.strftime("%Y-%m-%d"),
                    "date_label": target_date.strftime("%d/%m"),
                    "production_kwh": 0,
                    "consumption_kwh": 0
                })
        
        logger.info("Daily energy history generated", days=len(daily_data))
        
        return {
            "data": daily_data,
            "days": days,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error fetching daily energy history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


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