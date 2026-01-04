"""
Building Models for SunPulse

Defines the Building entity as the central concept:
- Users -> Buildings (N:M relationship)
- Buildings -> Devices (1:N relationship)
- Buildings -> Weather (1:N time series)
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Float, 
    ForeignKey, Text, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum as PyEnum

from .device import Base


# ==============================================================================
# Enums
# ==============================================================================

class UserBuildingRole(str, PyEnum):
    """Roles for user-building relationship"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class OnboardingStatus(str, PyEnum):
    """Status of user onboarding wizard"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# ==============================================================================
# SQLAlchemy Models
# ==============================================================================

class Building(Base):
    """
    Building entity - Central concept in SunPulse
    
    Represents a physical location (house, office, warehouse, etc.)
    where photovoltaic devices are installed.
    """
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Address information (from Google Places)
    address = Column(String(500), nullable=False)
    address_components = Column(JSONB)  # Structured address components
    place_id = Column(String(100))  # Google Place ID
    
    # GPS Coordinates
    latitude = Column(Float(precision=8))
    longitude = Column(Float(precision=8))
    
    # Settings
    timezone = Column(String(50), default="Europe/Rome")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))  # Auth0 user ID of creator
    
    # Relationships
    user_buildings = relationship(
        "UserBuilding", 
        back_populates="building", 
        cascade="all, delete-orphan"
    )
    devices = relationship(
        "BuildingDevice", 
        back_populates="building", 
        cascade="all, delete-orphan"
    )
    weather_data = relationship(
        "BuildingWeather", 
        back_populates="building", 
        cascade="all, delete-orphan",
        order_by="desc(BuildingWeather.fetched_at)"
    )
    
    def __repr__(self):
        return f"<Building(id={self.id}, name='{self.name}', address='{self.address}')>"


class UserBuilding(Base):
    """
    N:M relationship between Users and Buildings
    
    Allows multiple users to access the same building with different roles.
    """
    __tablename__ = "user_buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)  # Auth0 user ID
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    
    # Role
    role = Column(String(50), default=UserBuildingRole.MEMBER.value)
    
    # Invitation info
    invited_by = Column(String(255))  # Auth0 user ID of inviter
    invitation_email = Column(String(255))  # Email used for invitation
    invitation_token = Column(String(255))  # Token for accepting invitation
    invitation_accepted = Column(Boolean, default=True)
    
    # Metadata
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    building = relationship("Building", back_populates="user_buildings")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'building_id', name='uq_user_building'),
        Index('ix_user_buildings_user_id', 'user_id'),
        Index('ix_user_buildings_building_id', 'building_id'),
    )
    
    def __repr__(self):
        return f"<UserBuilding(user_id='{self.user_id}', building_id={self.building_id}, role='{self.role}')>"


class BuildingDevice(Base):
    """
    Devices associated with a building
    
    Links ZCS devices (by thing_key) to a specific building.
    """
    __tablename__ = "building_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    thing_key = Column(String(100), nullable=False, index=True)
    
    # Device info
    name = Column(String(255))
    device_type = Column(String(50), default="inverter")  # inverter, battery, meter
    
    # Status
    status = Column(String(20), default="unknown")  # online, offline, warning, unknown
    last_seen = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    building = relationship("Building", back_populates="devices")
    
    __table_args__ = (
        UniqueConstraint('building_id', 'thing_key', name='uq_building_device'),
        Index('ix_building_devices_thing_key', 'thing_key'),
    )
    
    def __repr__(self):
        return f"<BuildingDevice(building_id={self.building_id}, thing_key='{self.thing_key}')>"


class BuildingWeather(Base):
    """
    Weather data for a building
    
    Stores periodic weather updates fetched from weather API.
    """
    __tablename__ = "building_weather"
    
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    
    # Temperature
    temperature = Column(Float)  # °C
    feels_like = Column(Float)  # °C
    temp_min = Column(Float)  # °C
    temp_max = Column(Float)  # °C
    
    # Atmosphere
    humidity = Column(Integer)  # %
    pressure = Column(Integer)  # hPa
    
    # Wind
    wind_speed = Column(Float)  # m/s
    wind_deg = Column(Integer)  # degrees
    wind_gust = Column(Float)  # m/s
    
    # Conditions
    weather_condition = Column(String(50))  # clear, clouds, rain, snow, etc.
    weather_description = Column(String(100))  # Detailed description
    weather_icon = Column(String(20))  # Icon code from API
    
    # Clouds and visibility
    clouds = Column(Integer)  # % cloudiness
    visibility = Column(Integer)  # meters
    
    # Sun times
    sunrise = Column(DateTime)
    sunset = Column(DateTime)
    
    # Metadata
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    building = relationship("Building", back_populates="weather_data")
    
    __table_args__ = (
        Index('ix_building_weather_building_fetched', 'building_id', 'fetched_at'),
    )
    
    def __repr__(self):
        return f"<BuildingWeather(building_id={self.building_id}, temp={self.temperature}°C, fetched={self.fetched_at})>"


class UserOnboarding(Base):
    """
    Tracks user onboarding wizard progress
    
    Stores the current step and status of the onboarding wizard.
    """
    __tablename__ = "user_onboarding"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)  # Auth0 user ID
    
    # Wizard progress
    current_step = Column(Integer, default=1)
    status = Column(String(20), default=OnboardingStatus.NOT_STARTED.value)
    
    # Reference to building created during wizard
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    
    # Step data (temporary storage during wizard)
    step_data = Column(JSONB, default={})  # Stores form data for each step
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserOnboarding(user_id='{self.user_id}', step={self.current_step}, status='{self.status}')>"


# ==============================================================================
# Pydantic Models for API
# ==============================================================================

# --- Building Schemas ---

class BuildingBase(BaseModel):
    """Base schema for building"""
    name: str = Field(..., min_length=1, max_length=255, description="Nome edificio")
    address: str = Field(..., min_length=1, max_length=500, description="Indirizzo completo")


class BuildingCreate(BuildingBase):
    """Schema for creating a building"""
    place_id: Optional[str] = Field(None, description="Google Place ID")
    address_components: Optional[Dict[str, Any]] = Field(None, description="Componenti indirizzo strutturati")
    latitude: Optional[float] = Field(None, description="Latitudine")
    longitude: Optional[float] = Field(None, description="Longitudine")
    timezone: Optional[str] = Field("Europe/Rome", description="Fuso orario")


class BuildingUpdate(BaseModel):
    """Schema for updating a building"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    place_id: Optional[str] = None
    address_components: Optional[Dict[str, Any]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None


class BuildingResponse(BuildingBase):
    """Schema for building response"""
    id: int
    place_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    device_count: Optional[int] = 0
    current_temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    
    class Config:
        from_attributes = True


class BuildingListResponse(BaseModel):
    """Schema for list of buildings"""
    buildings: List[BuildingResponse]
    total: int


# --- User Building Schemas ---

class UserBuildingResponse(BaseModel):
    """Schema for user-building relationship"""
    id: int
    user_id: str
    building_id: int
    role: str
    joined_at: datetime
    building: Optional[BuildingResponse] = None
    
    class Config:
        from_attributes = True


class BuildingMemberResponse(BaseModel):
    """Schema for building member"""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    role: str
    joined_at: datetime
    invitation_accepted: bool


class InviteMemberRequest(BaseModel):
    """Schema for inviting a member to a building"""
    email: str = Field(..., description="Email dell'utente da invitare")
    role: str = Field(UserBuildingRole.MEMBER.value, description="Ruolo da assegnare")


class UpdateMemberRoleRequest(BaseModel):
    """Schema for updating member role"""
    role: str = Field(..., description="Nuovo ruolo")


# --- Building Device Schemas ---

class BuildingDeviceCreate(BaseModel):
    """Schema for adding a device to a building"""
    thing_key: str = Field(..., min_length=1, max_length=100, description="ZCS Thing Key")
    name: Optional[str] = Field(None, max_length=255, description="Nome dispositivo")
    device_type: Optional[str] = Field("inverter", description="Tipo dispositivo")


class BuildingDeviceResponse(BaseModel):
    """Schema for building device response"""
    id: int
    building_id: int
    thing_key: str
    name: Optional[str] = None
    device_type: str
    status: str
    last_seen: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# --- Weather Schemas ---

class BuildingWeatherResponse(BaseModel):
    """Schema for weather data response"""
    temperature: Optional[float] = Field(None, description="Temperatura °C")
    feels_like: Optional[float] = Field(None, description="Temperatura percepita °C")
    humidity: Optional[int] = Field(None, description="Umidità %")
    pressure: Optional[int] = Field(None, description="Pressione hPa")
    wind_speed: Optional[float] = Field(None, description="Velocità vento m/s")
    weather_condition: Optional[str] = Field(None, description="Condizione meteo")
    weather_description: Optional[str] = Field(None, description="Descrizione")
    weather_icon: Optional[str] = Field(None, description="Icona meteo")
    clouds: Optional[int] = Field(None, description="Nuvolosità %")
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BuildingWeatherHistoryResponse(BaseModel):
    """Schema for weather history"""
    building_id: int
    history: List[BuildingWeatherResponse]
    period_start: datetime
    period_end: datetime


# --- Onboarding Schemas ---

class OnboardingStatusResponse(BaseModel):
    """Schema for onboarding status"""
    user_id: str
    current_step: int
    status: str
    building_id: Optional[int] = None
    step_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class OnboardingStepUpdate(BaseModel):
    """Schema for updating onboarding step"""
    step_data: Dict[str, Any] = Field(default_factory=dict, description="Dati dello step")


class OnboardingDeviceValidation(BaseModel):
    """Schema for device validation request"""
    thing_key: str = Field(..., description="ZCS Thing Key da validare")


class OnboardingDeviceValidationResponse(BaseModel):
    """Schema for device validation response"""
    thing_key: str
    valid: bool
    device_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# --- Address Autocomplete Schemas ---

class AddressAutocompleteResult(BaseModel):
    """Schema for address autocomplete result"""
    place_id: str
    description: str
    main_text: str
    secondary_text: Optional[str] = None


class AddressAutocompleteResponse(BaseModel):
    """Schema for address autocomplete response"""
    results: List[AddressAutocompleteResult]


class AddressDetailsResponse(BaseModel):
    """Schema for address details"""
    place_id: str
    formatted_address: str
    address_components: Dict[str, Any]
    latitude: float
    longitude: float
    timezone: Optional[str] = None
