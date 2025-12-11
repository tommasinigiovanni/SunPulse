"""
ZCS API Service - Integrazione con ZCS Azzurro Portal
"""
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import structlog
import json

from ..config.settings import get_settings
from ..utils.circuit_breaker import CircuitBreaker

logger = structlog.get_logger()

class ZCSEndpoint(Enum):
    """Endpoint disponibili ZCS API"""
    REALTIME_DATA = "realtimeData"
    HISTORIC_DATA = "historicData"
    DEVICE_ALARM = "deviceAlarm"
    HISTORIC_ALARM = "deviceHistoricAlarm"

class ZCSAPIService:
    """Servizio per interagire con le API ZCS Azzurro Portal"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.ZCS_API_URL
        self.auth_header = self.settings.ZCS_API_AUTH
        self.client_code = self.settings.ZCS_CLIENT_CODE
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            service_name="zcs_api"
        )
        
        # Configurazione client HTTP
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        
    async def _make_request(self, endpoint: ZCSEndpoint, params: Dict[str, Any]) -> Dict[str, Any]:
        """Effettua una richiesta alle API ZCS con protezione circuit breaker"""
        
        async def _http_request():
            headers = {
                "Authorization": self.auth_header,
                "client": self.client_code,
                "Content-Type": "application/json"
            }
            
            # Payload ZCS API format
            payload = {
                endpoint.value: {
                    "command": endpoint.value,
                    "params": params
                }
            }
            
            logger.info(
                "ZCS API Request",
                endpoint=endpoint.value,
                thing_keys=params.get("thingKey", "unknown"),
                payload_size=len(json.dumps(payload))
            )
            
            async with httpx.AsyncClient(
                timeout=self.timeout,
                limits=self.limits
            ) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(
                    "ZCS API Response",
                    endpoint=endpoint.value,
                    status_code=response.status_code,
                    response_size=len(response.text)
                )
                
                return result
        
        # Usa circuit breaker per la protezione
        return await self.circuit_breaker.call(_http_request)
    
    async def get_realtime_data(self, thing_keys: List[str], required_values: str = "*") -> Dict[str, Any]:
        """
        Ottieni dati in tempo reale per i dispositivi specificati
        
        Args:
            thing_keys: Lista delle chiavi dispositivo
            required_values: Valori richiesti ("*" per tutti)
            
        Returns:
            Dati in tempo reale dal ZCS Portal
        """
        try:
            # ZCS API supports only one thingKey per request
            results = {}
            
            for thing_key in thing_keys:
                params = {
                    "thingKey": thing_key,
                    "requiredValues": required_values
                }
                
                result = await self._make_request(ZCSEndpoint.REALTIME_DATA, params)
                results[thing_key] = result
                
                # Rate limiting - aspetta tra le richieste
                if len(thing_keys) > 1:
                    await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "data": results,
                "timestamp": datetime.utcnow().isoformat(),
                "device_count": len(thing_keys)
            }
            
        except Exception as e:
            logger.error(
                "Error fetching realtime data",
                error=str(e),
                thing_keys=thing_keys
            )
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_historic_data(
        self, 
        thing_keys: List[str], 
        start_date: datetime, 
        end_date: datetime,
        resolution: str = "1h"
    ) -> Dict[str, Any]:
        """
        Ottieni dati storici per i dispositivi (max 24h window per richiesta)
        
        Args:
            thing_keys: Lista delle chiavi dispositivo
            start_date: Data inizio
            end_date: Data fine
            resolution: Risoluzione dati
            
        Returns:
            Dati storici dal ZCS Portal
        """
        try:
            # Verifica che la finestra sia <= 24h
            time_diff = end_date - start_date
            if time_diff > timedelta(hours=24):
                logger.warning(
                    "Time window > 24h, splitting request",
                    start=start_date.isoformat(),
                    end=end_date.isoformat(),
                    hours=time_diff.total_seconds() / 3600
                )
                
                # Suddividi in finestre di 24h
                return await self._get_historic_data_chunked(
                    thing_keys, start_date, end_date, resolution
                )
            
            results = {}
            
            for thing_key in thing_keys:
                # Formato date corretto per ZCS API: ISO8601 con Z
                params = {
                    "thingKey": thing_key,
                    "requiredValues": "*",
                    "start": start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "end": end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                }
                
                result = await self._make_request(ZCSEndpoint.HISTORIC_DATA, params)
                results[thing_key] = result
                
                # Rate limiting
                if len(thing_keys) > 1:
                    await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "data": results,
                "timestamp": datetime.utcnow().isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "resolution": resolution
                }
            }
            
        except Exception as e:
            logger.error(
                "Error fetching historic data",
                error=str(e),
                thing_keys=thing_keys,
                start=start_date.isoformat(),
                end=end_date.isoformat()
            )
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_historic_data_chunked(
        self,
        thing_keys: List[str],
        start_date: datetime,
        end_date: datetime,
        resolution: str
    ) -> Dict[str, Any]:
        """Suddivide richieste di dati storici in chunks di 24h"""
        
        all_results = {}
        current_start = start_date
        
        while current_start < end_date:
            current_end = min(current_start + timedelta(hours=23), end_date)
            
            chunk_result = await self.get_historic_data(
                thing_keys, current_start, current_end, resolution
            )
            
            if chunk_result["success"]:
                # Merge dei risultati
                for thing_key, data in chunk_result["data"].items():
                    if thing_key not in all_results:
                        all_results[thing_key] = data
                    else:
                        # Merge dei dati (implementazione dipende dalla struttura ZCS)
                        # TODO: implementare merge logic specifica per ZCS response
                        pass
            
            current_start = current_end + timedelta(minutes=1)
        
        return {
            "success": True,
            "data": all_results,
            "timestamp": datetime.utcnow().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "resolution": resolution,
                "chunked": True
            }
        }
    
    async def get_device_alarms(self, thing_keys: List[str]) -> Dict[str, Any]:
        """
        Ottieni stato allarmi corrente per i dispositivi
        
        Args:
            thing_keys: Lista delle chiavi dispositivo
            
        Returns:
            Stato allarmi corrente
        """
        try:
            results = {}
            
            for thing_key in thing_keys:
                params = {
                    "thingKey": thing_key,
                    "requiredValues": "*"
                }
                
                result = await self._make_request(ZCSEndpoint.DEVICE_ALARM, params)
                results[thing_key] = result
                
                # Rate limiting
                if len(thing_keys) > 1:
                    await asyncio.sleep(0.3)
            
            return {
                "success": True,
                "data": results,
                "timestamp": datetime.utcnow().isoformat(),
                "device_count": len(thing_keys)
            }
            
        except Exception as e:
            logger.error(
                "Error fetching device alarms",
                error=str(e),
                thing_keys=thing_keys
            )
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_historic_alarms(
        self,
        thing_keys: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Ottieni storico allarmi per i dispositivi
        
        Args:
            thing_keys: Lista delle chiavi dispositivo  
            start_date: Data inizio
            end_date: Data fine
            
        Returns:
            Storico allarmi
        """
        try:
            results = {}
            
            for thing_key in thing_keys:
                # Formato date corretto per ZCS API: ISO8601 con Z
                params = {
                    "thingKey": thing_key,
                    "requiredValues": "*",
                    "start": start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "end": end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                }
                
                result = await self._make_request(ZCSEndpoint.HISTORIC_ALARM, params)
                results[thing_key] = result
                
                # Rate limiting
                if len(thing_keys) > 1:
                    await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "data": results,
                "timestamp": datetime.utcnow().isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(
                "Error fetching historic alarms",
                error=str(e),
                thing_keys=thing_keys,
                start=start_date.isoformat(),
                end=end_date.isoformat()
            )
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica connettività ZCS API"""
        try:
            # Test con payload minimo
            test_payload = {
                "test": {
                    "command": "ping"
                }
            }
            
            headers = {
                "Authorization": self.auth_header,
                "client": self.client_code,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=test_payload
                )
                
                return {
                    "healthy": response.status_code < 500,
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "circuit_breaker_state": self.circuit_breaker.state.value
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "circuit_breaker_state": self.circuit_breaker.state.value
            }

# Istanza globale del servizio ZCS API
_zcs_service = None

async def get_zcs_service() -> ZCSAPIService:
    """Ottieni istanza del servizio ZCS API"""
    global _zcs_service
    if _zcs_service is None:
        _zcs_service = ZCSAPIService()
    return _zcs_service 