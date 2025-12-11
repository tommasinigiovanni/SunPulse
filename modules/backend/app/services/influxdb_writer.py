"""
InfluxDB Writer Service - Gestione scrittura dati time-series
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import structlog

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError

from ..config.settings import get_settings
from ..models.device import DeviceDataPoint

logger = structlog.get_logger()

class InfluxDBWriter:
    """Servizio per scrivere dati time-series in InfluxDB"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[InfluxDBClient] = None
        self.write_api = None
        self.bucket = self.settings.INFLUXDB_DB
        self.org = "sunpulse"
        
        # Statistiche
        self.stats = {
            "points_written": 0,
            "write_errors": 0,
            "batch_writes": 0,
            "last_write": None
        }
    
    async def init(self):
        """Inizializza connessione InfluxDB"""
        try:
            # Configurazione client InfluxDB v2
            self.client = InfluxDBClient(
                url=self.settings.influxdb_url,
                token=self.settings.INFLUXDB_PASSWORD,  # In v2 si usa token
                org=self.org,
                timeout=30000,  # 30 secondi
                enable_gzip=True,
                debug=self.settings.DEBUG
            )
            
            # Test connessione
            health = self.client.health()
            if health.status == "pass":
                logger.info("InfluxDB connection established", url=self.settings.influxdb_url)
                
                # Inizializza write API
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                
                return True
            else:
                logger.error("InfluxDB health check failed", status=health.status)
                return False
                
        except Exception as e:
            logger.error("Failed to connect to InfluxDB", error=str(e))
            self.client = None
            return False
    
    async def write_points(self, data_points: List[DeviceDataPoint]) -> bool:
        """
        Scrive una lista di data points in InfluxDB
        
        Args:
            data_points: Lista di DeviceDataPoint
            
        Returns:
            True se successo, False altrimenti
        """
        if not self.client or not self.write_api:
            logger.error("InfluxDB client not initialized")
            return False
        
        if not data_points:
            logger.debug("No data points to write")
            return True
        
        try:
            # Converte DeviceDataPoint in InfluxDB Points
            influx_points = []
            
            for dp in data_points:
                # Crea Point InfluxDB
                point = Point(dp.measurement)
                
                # Aggiungi tags
                for tag_key, tag_value in dp.tags.items():
                    point = point.tag(tag_key, str(tag_value))
                
                # Aggiungi fields
                for field_key, field_value in dp.fields.items():
                    point = point.field(field_key, field_value)
                
                # Imposta timestamp
                point = point.time(dp.timestamp)
                
                influx_points.append(point)
            
            # Scrivi in batch
            self.write_api.write(
                bucket=self.bucket,
                org=self.org,
                record=influx_points
            )
            
            # Aggiorna statistiche
            self.stats["points_written"] += len(data_points)
            self.stats["batch_writes"] += 1
            self.stats["last_write"] = datetime.utcnow().isoformat()
            
            logger.info(
                "Data points written to InfluxDB",
                count=len(data_points),
                bucket=self.bucket,
                measurements=[dp.measurement for dp in data_points]
            )
            
            return True
            
        except InfluxDBError as e:
            self.stats["write_errors"] += 1
            logger.error(
                "InfluxDB write error",
                error=str(e),
                points_count=len(data_points)
            )
            return False
            
        except Exception as e:
            self.stats["write_errors"] += 1
            logger.error(
                "Unexpected error writing to InfluxDB",
                error=str(e),
                points_count=len(data_points)
            )
            return False
    
    async def write_single_point(self, data_point: DeviceDataPoint) -> bool:
        """
        Scrive un singolo data point
        
        Args:
            data_point: DeviceDataPoint da scrivere
            
        Returns:
            True se successo
        """
        return await self.write_points([data_point])
    
    async def write_power_data(
        self,
        device_key: str,
        device_type: str,
        power_data: Dict[str, float],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Scrive dati di potenza per un dispositivo
        
        Args:
            device_key: Chiave dispositivo
            device_type: Tipo dispositivo
            power_data: Dizionario con dati di potenza
            timestamp: Timestamp (default: now)
            
        Returns:
            True se successo
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        data_point = DeviceDataPoint(
            measurement="power_data",
            tags={
                "device_key": device_key,
                "device_type": device_type
            },
            fields=power_data,
            timestamp=timestamp
        )
        
        return await self.write_single_point(data_point)
    
    async def write_energy_data(
        self,
        device_key: str,
        device_type: str,
        energy_data: Dict[str, float],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Scrive dati di energia per un dispositivo
        
        Args:
            device_key: Chiave dispositivo
            device_type: Tipo dispositivo
            energy_data: Dizionario con dati di energia
            timestamp: Timestamp (default: now)
            
        Returns:
            True se successo
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        data_point = DeviceDataPoint(
            measurement="energy_data",
            tags={
                "device_key": device_key,
                "device_type": device_type
            },
            fields=energy_data,
            timestamp=timestamp
        )
        
        return await self.write_single_point(data_point)
    
    async def write_battery_data(
        self,
        device_key: str,
        battery_data: Dict[str, float],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Scrive dati batteria
        
        Args:
            device_key: Chiave dispositivo
            battery_data: Dizionario con dati batteria
            timestamp: Timestamp (default: now)
            
        Returns:
            True se successo
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        data_point = DeviceDataPoint(
            measurement="battery_data",
            tags={
                "device_key": device_key,
                "device_type": "battery"
            },
            fields=battery_data,
            timestamp=timestamp
        )
        
        return await self.write_single_point(data_point)
    
    async def write_alarm_data(
        self,
        device_key: str,
        device_type: str,
        alarm_code: str,
        alarm_type: str,
        severity: str,
        is_active: bool = True,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Scrive dati allarme
        
        Args:
            device_key: Chiave dispositivo
            device_type: Tipo dispositivo
            alarm_code: Codice allarme
            alarm_type: Tipo allarme
            severity: Severità (low, medium, high, critical)
            is_active: Se l'allarme è attivo
            timestamp: Timestamp (default: now)
            
        Returns:
            True se successo
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        data_point = DeviceDataPoint(
            measurement="alarm_data",
            tags={
                "device_key": device_key,
                "device_type": device_type,
                "alarm_code": alarm_code,
                "alarm_type": alarm_type,
                "severity": severity
            },
            fields={
                "is_active": 1 if is_active else 0,
                "alarm_numeric_code": hash(alarm_code) % 10000
            },
            timestamp=timestamp
        )
        
        return await self.write_single_point(data_point)
    
    async def query_data(
        self,
        measurement: str,
        device_key: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        aggregation: Optional[str] = None,
        window: str = "1h"
    ) -> List[Dict[str, Any]]:
        """
        Query dati da InfluxDB
        
        Args:
            measurement: Nome measurement
            device_key: Filtro per device_key (opzionale)
            start_time: Tempo inizio
            end_time: Tempo fine
            aggregation: Tipo aggregazione (mean, sum, max, min)
            window: Finestra aggregazione
            
        Returns:
            Lista di record
        """
        if not self.client:
            logger.error("InfluxDB client not initialized")
            return []
        
        try:
            # Costruisce query Flux
            query = f'from(bucket: "{self.bucket}")'
            
            # Filtro temporale
            if start_time:
                query += f'  |> range(start: {start_time.isoformat()}Z'
                if end_time:
                    query += f', stop: {end_time.isoformat()}Z'
                query += ')'
            else:
                query += '  |> range(start: -24h)'  # Ultime 24h di default
            
            # Filtro measurement
            query += f'  |> filter(fn: (r) => r._measurement == "{measurement}")'
            
            # Filtro device_key se specificato
            if device_key:
                query += f'  |> filter(fn: (r) => r.device_key == "{device_key}")'
            
            # Aggregazione se richiesta
            if aggregation:
                query += f'  |> aggregateWindow(every: {window}, fn: {aggregation})'
            
            # Esegui query
            query_api = self.client.query_api()
            result = query_api.query(query=query, org=self.org)
            
            # Converte risultato in lista di dict
            records = []
            for table in result:
                for record in table.records:
                    records.append({
                        "time": record.get_time(),
                        "measurement": record.get_measurement(),
                        "field": record.get_field(),
                        "value": record.get_value(),
                        "tags": {k: v for k, v in record.values.items() if k.startswith("tag_") or k in ["device_key", "device_type"]}
                    })
            
            logger.info(
                "InfluxDB query executed",
                measurement=measurement,
                device_key=device_key,
                records_count=len(records)
            )
            
            return records
            
        except Exception as e:
            logger.error(
                "Error querying InfluxDB",
                error=str(e),
                measurement=measurement,
                device_key=device_key
            )
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Ottieni statistiche del writer"""
        return {
            "connected": self.client is not None,
            "bucket": self.bucket,
            "org": self.org,
            **self.stats
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica salute connessione InfluxDB"""
        try:
            if not self.client:
                return {"healthy": False, "error": "Client not initialized"}
            
            health = self.client.health()
            
            return {
                "healthy": health.status == "pass",
                "status": health.status,
                "version": health.version if hasattr(health, 'version') else "unknown",
                "stats": self.get_stats()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def close(self):
        """Chiudi connessione InfluxDB"""
        if self.client:
            self.client.close()
            logger.info("InfluxDB connection closed")

# Istanza globale del writer InfluxDB
_influxdb_writer = None

async def get_influxdb_writer() -> InfluxDBWriter:
    """Ottieni istanza del writer InfluxDB"""
    global _influxdb_writer
    if _influxdb_writer is None:
        _influxdb_writer = InfluxDBWriter()
        await _influxdb_writer.init()
    return _influxdb_writer 