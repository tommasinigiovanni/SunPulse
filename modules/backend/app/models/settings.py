"""
User Settings Model for SunPulse
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .device import Base


class UserSettings(Base):
    """User settings stored in PostgreSQL, linked to Auth0 user ID"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)  # Auth0 sub
    
    # Generale
    system_name = Column(String(255), default="Il mio impianto")
    language = Column(String(10), default="it")
    timezone = Column(String(50), default="Europe/Rome")
    currency = Column(String(10), default="EUR")
    energy_price = Column(Float, default=0.25)
    sell_price = Column(Float, default=0.10)
    
    # Notifiche
    notification_email = Column(String(255), nullable=True)
    notify_critical_alarms = Column(Boolean, default=True)
    notify_warnings = Column(Boolean, default=True)
    notify_daily_report = Column(Boolean, default=False)
    notify_weekly_report = Column(Boolean, default=True)
    battery_low_threshold = Column(Integer, default=20)
    battery_critical_threshold = Column(Integer, default=10)
    
    # API Intervals
    realtime_interval = Column(Integer, default=60)  # secondi
    historical_interval = Column(Integer, default=15)  # minuti
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserSettings(user_id='{self.user_id}', system_name='{self.system_name}')>"


# ==============================================================================
# Pydantic Models for API
# ==============================================================================

class UserSettingsBase(BaseModel):
    """Base schema for user settings"""
    # Generale
    system_name: Optional[str] = Field("Il mio impianto", description="Nome impianto")
    language: Optional[str] = Field("it", description="Lingua")
    timezone: Optional[str] = Field("Europe/Rome", description="Fuso orario")
    currency: Optional[str] = Field("EUR", description="Valuta")
    energy_price: Optional[float] = Field(0.25, description="Prezzo acquisto energia €/kWh")
    sell_price: Optional[float] = Field(0.10, description="Prezzo vendita energia €/kWh")
    
    # Notifiche
    notification_email: Optional[str] = Field(None, description="Email notifiche")
    notify_critical_alarms: Optional[bool] = Field(True, description="Notifica allarmi critici")
    notify_warnings: Optional[bool] = Field(True, description="Notifica avvisi")
    notify_daily_report: Optional[bool] = Field(False, description="Report giornaliero")
    notify_weekly_report: Optional[bool] = Field(True, description="Report settimanale")
    battery_low_threshold: Optional[int] = Field(20, description="Soglia batteria bassa %")
    battery_critical_threshold: Optional[int] = Field(10, description="Soglia batteria critica %")
    
    # API
    realtime_interval: Optional[int] = Field(60, description="Intervallo dati realtime (secondi)")
    historical_interval: Optional[int] = Field(15, description="Intervallo dati storici (minuti)")


class UserSettingsUpdate(UserSettingsBase):
    """Schema for updating user settings - all fields optional"""
    pass


class UserSettingsResponse(UserSettingsBase):
    """Schema for user settings response"""
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DeviceInfo(BaseModel):
    """Device info for settings page"""
    thing_key: str
    name: str
    device_type: str
    status: str
    last_update: Optional[str] = None


class ApiStatusResponse(BaseModel):
    """API connection status"""
    endpoint: str
    connected: bool
    last_sync: Optional[str] = None
    client_code_configured: bool
    error: Optional[str] = None
