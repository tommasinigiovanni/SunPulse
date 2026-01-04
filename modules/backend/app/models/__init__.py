"""
SunPulse Models

This module exports all SQLAlchemy models and Pydantic schemas.
"""

# Device models
from .device import (
    Base,
    DeviceType,
    DeviceStatus,
    AlarmSeverity,
    AlarmCategory,
    Device,
    DeviceConfiguration,
    DeviceAlarm,
    DailyEnergy,
    AlarmHistory,
    DeviceBase,
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceAlarmResponse,
    DeviceDataPoint,
    PowerDataPoint,
    EnergyDataPoint,
    BatteryDataPoint,
    AlarmDataPoint,
    AlarmResponse,
    AlarmLevel,
    DailyEnergyBase,
    DailyEnergyResponse,
    DailyEnergySummary,
    parse_zcs_realtime_to_models,
)

# Settings models
from .settings import (
    UserSettings,
    UserSettingsBase,
    UserSettingsUpdate,
    UserSettingsResponse,
    DeviceInfo,
    ApiStatusResponse,
)

# Building models
from .building import (
    UserBuildingRole,
    OnboardingStatus,
    Building,
    UserBuilding,
    BuildingDevice,
    BuildingWeather,
    UserOnboarding,
    BuildingBase,
    BuildingCreate,
    BuildingUpdate,
    BuildingResponse,
    BuildingListResponse,
    UserBuildingResponse,
    BuildingMemberResponse,
    InviteMemberRequest,
    UpdateMemberRoleRequest,
    BuildingDeviceCreate,
    BuildingDeviceResponse,
    BuildingWeatherResponse,
    BuildingWeatherHistoryResponse,
    OnboardingStatusResponse,
    OnboardingStepUpdate,
    OnboardingDeviceValidation,
    OnboardingDeviceValidationResponse,
    AddressAutocompleteResult,
    AddressAutocompleteResponse,
    AddressDetailsResponse,
)

# Audit models
from .audit import (
    AuditLog,
    AuditLogCreate,
    AuditLogResponse,
)

__all__ = [
    # Base
    "Base",
    
    # Device Enums
    "DeviceType",
    "DeviceStatus",
    "AlarmSeverity",
    "AlarmCategory",
    
    # Device Models
    "Device",
    "DeviceConfiguration",
    "DeviceAlarm",
    "DailyEnergy",
    "AlarmHistory",
    
    # Device Schemas
    "DeviceBase",
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    "DeviceAlarmResponse",
    
    # Data Points
    "DeviceDataPoint",
    "PowerDataPoint",
    "EnergyDataPoint",
    "BatteryDataPoint",
    "AlarmDataPoint",
    
    # Alarm Schemas
    "AlarmResponse",
    "AlarmLevel",
    
    # Daily Energy Schemas
    "DailyEnergyBase",
    "DailyEnergyResponse",
    "DailyEnergySummary",
    
    # Utility Functions
    "parse_zcs_realtime_to_models",
    
    # Settings Models
    "UserSettings",
    "UserSettingsBase",
    "UserSettingsUpdate",
    "UserSettingsResponse",
    "DeviceInfo",
    "ApiStatusResponse",
    
    # Building Enums
    "UserBuildingRole",
    "OnboardingStatus",
    
    # Building Models
    "Building",
    "UserBuilding",
    "BuildingDevice",
    "BuildingWeather",
    "UserOnboarding",
    
    # Building Schemas
    "BuildingBase",
    "BuildingCreate",
    "BuildingUpdate",
    "BuildingResponse",
    "BuildingListResponse",
    "UserBuildingResponse",
    "BuildingMemberResponse",
    "InviteMemberRequest",
    "UpdateMemberRoleRequest",
    "BuildingDeviceCreate",
    "BuildingDeviceResponse",
    "BuildingWeatherResponse",
    "BuildingWeatherHistoryResponse",
    
    # Onboarding Schemas
    "OnboardingStatusResponse",
    "OnboardingStepUpdate",
    "OnboardingDeviceValidation",
    "OnboardingDeviceValidationResponse",
    
    # Address Schemas
    "AddressAutocompleteResult",
    "AddressAutocompleteResponse",
    "AddressDetailsResponse",
    
    # Audit Models
    "AuditLog",
    "AuditLogCreate",
    "AuditLogResponse",
]
