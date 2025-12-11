"""
Data Models per dispositivi e dati energetici
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Float, Enum, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum as PyEnum
from pydantic import BaseModel, Field
from dataclasses import dataclass

Base = declarative_base()

class DeviceType(PyEnum):
    """Tipi di dispositivo supportati"""
    INVERTER = "inverter"
    BATTERY = "battery"
    METER = "meter"
    SENSOR = "sensor"
    GATEWAY = "gateway"

class DeviceStatus(PyEnum):
    """Stati del dispositivo"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNKNOWN = "unknown"

class AlarmSeverity(PyEnum):
    """Livelli di severità allarmi"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlarmCategory(PyEnum):
    """Categorie di allarmi"""
    SYSTEM = "system"
    POWER = "power"
    BATTERY = "battery"
    COMMUNICATION = "communication"
    MAINTENANCE = "maintenance"
    WEATHER = "weather"

# ==============================================================================
# SQLAlchemy Models (PostgreSQL)
# ==============================================================================

class Device(Base):
    """Modello dispositivo nel database relazionale"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    thing_key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.UNKNOWN)
    
    # Informazioni fisiche
    location = Column(String(255))
    manufacturer = Column(String(100))
    model = Column(String(100))
    firmware_version = Column(String(50))
    installation_date = Column(Date)
    
    # Configurazione
    config_json = Column(JSON)  # Configurazione flessibile in JSON
    
    # Metadati
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relazioni
    configurations = relationship("DeviceConfiguration", back_populates="device", cascade="all, delete-orphan")
    alarms = relationship("DeviceAlarm", back_populates="device", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Device(id={self.id}, thing_key='{self.thing_key}', type='{self.device_type.value}')>"

class DeviceConfiguration(Base):
    """Configurazioni specifiche del dispositivo"""
    __tablename__ = "device_configurations"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    config_key = Column(String(100), nullable=False)
    config_value = Column(String(500))
    data_type = Column(String(20), default="string")  # string, number, boolean, json
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    device = relationship("Device", back_populates="configurations")
    
    __table_args__ = (
        {"extend_existing": True}
    )

class DeviceAlarm(Base):
    """Allarmi e alert dei dispositivi"""
    __tablename__ = "device_alarms"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    
    alarm_code = Column(String(50), nullable=False)
    alarm_type = Column(String(100))
    severity = Column(Enum(AlarmSeverity), default=AlarmSeverity.MEDIUM)
    message = Column(String(500))
    description = Column(String(1000))
    
    # Timing
    triggered_at = Column(DateTime, nullable=False)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Stato
    is_active = Column(Boolean, default=True)
    acknowledged_by = Column(String(255))  # User ID o sistema
    
    # Metadata
    raw_data = Column(JSON)  # Dati originali ZCS
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relazioni
    device = relationship("Device", back_populates="alarms")

# ==============================================================================
# Pydantic Models (API & Validation)
# ==============================================================================

class DeviceBase(BaseModel):
    """Schema base per dispositivo"""
    thing_key: str = Field(..., description="Chiave univoca dispositivo ZCS")
    name: str = Field(..., description="Nome dispositivo")
    device_type: DeviceType = Field(..., description="Tipo dispositivo")
    location: Optional[str] = Field(None, description="Ubicazione")
    manufacturer: Optional[str] = Field(None, description="Produttore")
    model: Optional[str] = Field(None, description="Modello")

class DeviceCreate(DeviceBase):
    """Schema per creazione dispositivo"""
    firmware_version: Optional[str] = None
    installation_date: Optional[str] = None  # ISO date string
    config_json: Optional[Dict[str, Any]] = None

class DeviceUpdate(BaseModel):
    """Schema per aggiornamento dispositivo"""
    name: Optional[str] = None
    status: Optional[DeviceStatus] = None
    location: Optional[str] = None
    firmware_version: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None

class DeviceResponse(DeviceBase):
    """Schema risposta dispositivo"""
    id: int
    status: DeviceStatus
    created_at: datetime
    updated_at: datetime
    last_seen: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

class DeviceAlarmResponse(BaseModel):
    """Schema risposta allarmi dispositivo"""
    id: int
    device_id: int
    alarm_code: str
    alarm_type: Optional[str]
    severity: AlarmSeverity
    message: Optional[str]
    triggered_at: datetime
    is_active: bool
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ==============================================================================
# InfluxDB Data Models (Time Series)
# ==============================================================================

@dataclass
class DeviceDataPoint:
    """Punto dati time-series per InfluxDB"""
    measurement: str
    tags: Dict[str, str]
    fields: Dict[str, float]
    timestamp: datetime
    
    def to_influx_point(self) -> Dict[str, Any]:
        """Converte in formato InfluxDB Point"""
        return {
            "measurement": self.measurement,
            "tags": self.tags,
            "fields": self.fields,
            "time": self.timestamp
        }

class PowerDataPoint(BaseModel):
    """Dati di potenza in tempo reale"""
    device_key: str
    device_type: str
    power_generating: Optional[float] = Field(None, description="Potenza generata (W)")
    power_consuming: Optional[float] = Field(None, description="Potenza consumata (W)")
    power_grid: Optional[float] = Field(None, description="Potenza da/verso rete (W)")
    power_battery: Optional[float] = Field(None, description="Potenza batteria (W)")
    voltage: Optional[float] = Field(None, description="Tensione (V)")
    current: Optional[float] = Field(None, description="Corrente (A)")
    frequency: Optional[float] = Field(None, description="Frequenza (Hz)")
    temperature: Optional[float] = Field(None, description="Temperatura (°C)")
    timestamp: datetime
    
    def to_influx_point(self) -> DeviceDataPoint:
        """Converte in DeviceDataPoint per InfluxDB"""
        tags = {
            "device_key": self.device_key,
            "device_type": self.device_type
        }
        
        fields = {}
        for field_name, value in self.dict(exclude={'device_key', 'device_type', 'timestamp'}).items():
            if value is not None:
                fields[field_name] = value
        
        return DeviceDataPoint(
            measurement="power_data",
            tags=tags,
            fields=fields,
            timestamp=self.timestamp
        )

class EnergyDataPoint(BaseModel):
    """Dati di energia accumulata"""
    device_key: str
    device_type: str
    energy_total: Optional[float] = Field(None, description="Energia totale prodotta (kWh)")
    energy_daily: Optional[float] = Field(None, description="Energia giornaliera (kWh)")
    energy_monthly: Optional[float] = Field(None, description="Energia mensile (kWh)")
    energy_yearly: Optional[float] = Field(None, description="Energia annuale (kWh)")
    energy_consumed_daily: Optional[float] = Field(None, description="Energia consumata giornaliera (kWh)")
    energy_exported: Optional[float] = Field(None, description="Energia esportata (kWh)")
    energy_imported: Optional[float] = Field(None, description="Energia importata (kWh)")
    timestamp: datetime
    
    def to_influx_point(self) -> DeviceDataPoint:
        """Converte in DeviceDataPoint per InfluxDB"""
        tags = {
            "device_key": self.device_key,
            "device_type": self.device_type
        }
        
        fields = {}
        for field_name, value in self.dict(exclude={'device_key', 'device_type', 'timestamp'}).items():
            if value is not None:
                fields[field_name] = value
        
        return DeviceDataPoint(
            measurement="energy_data",
            tags=tags,
            fields=fields,
            timestamp=self.timestamp
        )

class BatteryDataPoint(BaseModel):
    """Dati specifici batteria"""
    device_key: str
    device_type: str = "battery"
    soc: Optional[float] = Field(None, description="State of Charge (%)")
    voltage: Optional[float] = Field(None, description="Tensione batteria (V)")
    current: Optional[float] = Field(None, description="Corrente batteria (A)")
    temperature: Optional[float] = Field(None, description="Temperatura batteria (°C)")
    cycle_count: Optional[int] = Field(None, description="Numero cicli")
    health: Optional[float] = Field(None, description="Salute batteria (%)")
    charge_power: Optional[float] = Field(None, description="Potenza carica (W)")
    discharge_power: Optional[float] = Field(None, description="Potenza scarica (W)")
    remaining_time: Optional[float] = Field(None, description="Tempo rimanente (h)")
    timestamp: datetime
    
    def to_influx_point(self) -> DeviceDataPoint:
        """Converte in DeviceDataPoint per InfluxDB"""
        tags = {
            "device_key": self.device_key,
            "device_type": self.device_type
        }
        
        fields = {}
        for field_name, value in self.dict(exclude={'device_key', 'device_type', 'timestamp'}).items():
            if value is not None:
                fields[field_name] = value
        
        return DeviceDataPoint(
            measurement="battery_data",
            tags=tags,
            fields=fields,
            timestamp=self.timestamp
        )

class AlarmDataPoint(BaseModel):
    """Dati allarmi time-series"""
    device_key: str
    device_type: str
    alarm_code: str
    alarm_type: str
    severity: AlarmSeverity
    message: Optional[str] = None
    is_active: bool = True
    timestamp: datetime
    
    def to_influx_point(self) -> DeviceDataPoint:
        """Converte in DeviceDataPoint per InfluxDB"""
        tags = {
            "device_key": self.device_key,
            "device_type": self.device_type,
            "alarm_code": self.alarm_code,
            "alarm_type": self.alarm_type,
            "severity": self.severity.value
        }
        
        fields = {
            "is_active": 1 if self.is_active else 0,
            "alarm_numeric_code": hash(self.alarm_code) % 10000  # Numeric representation
        }
        
        if self.message:
            # Store message length as numeric field
            fields["message_length"] = len(self.message)
        
        return DeviceDataPoint(
            measurement="alarm_data",
            tags=tags,
            fields=fields,
            timestamp=self.timestamp
        )

# ==============================================================================
# Utility Functions
# ==============================================================================

def parse_zcs_realtime_to_models(zcs_data: Dict[str, Any], device_key: str) -> List[DeviceDataPoint]:
    """
    Converte dati ZCS realtime in modelli dati
    
    Args:
        zcs_data: Dati grezzi da ZCS API
        device_key: Chiave dispositivo
        
    Returns:
        Lista di DeviceDataPoint
    """
    data_points = []
    timestamp = datetime.utcnow()
    
    # TODO: Implementare parsing specifico per formato ZCS
    # Questa è una implementazione di esempio
    
    if "realtimeData" in zcs_data:
        realtime = zcs_data["realtimeData"]
        
        # Power data
        power_data = PowerDataPoint(
            device_key=device_key,
            device_type="inverter",  # Default, da determinare dal device
            power_generating=realtime.get("power_generating"),
            power_consuming=realtime.get("power_consuming"),
            voltage=realtime.get("voltage"),
            current=realtime.get("current"),
            timestamp=timestamp
        )
        data_points.append(power_data.to_influx_point())
        
        # Battery data se presente
        if "battery" in realtime:
            battery_data = BatteryDataPoint(
                device_key=device_key,
                soc=realtime["battery"].get("soc"),
                voltage=realtime["battery"].get("voltage"),
                temperature=realtime["battery"].get("temperature"),
                timestamp=timestamp
            )
            data_points.append(battery_data.to_influx_point())
    
    return data_points 

# ==============================================================================
# Compatibility Aliases and Additional Models
# ==============================================================================

class AlarmResponse(BaseModel):
    """Schema risposta allarmi per API"""
    id: str = Field(..., description="ID univoco allarme")
    device_thing_key: str = Field(..., description="Chiave dispositivo")
    device_name: str = Field(..., description="Nome dispositivo")
    code: str = Field(..., description="Codice allarme")
    message: str = Field(..., description="Messaggio allarme")
    level: AlarmSeverity = Field(..., description="Livello severità")
    category: AlarmCategory = Field(..., description="Categoria allarme")
    active: bool = Field(True, description="Allarme attivo")
    acknowledged: bool = Field(False, description="Allarme riconosciuto")
    triggered_at: datetime = Field(..., description="Timestamp attivazione")
    description: Optional[str] = Field(None, description="Descrizione dettagliata")
    suggested_action: Optional[str] = Field(None, description="Azione suggerita")
    
    class Config:
        from_attributes = True

# Aliases for backward compatibility
AlarmLevel = AlarmSeverity  # Alias per compatibilità