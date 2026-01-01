"""
User Settings Endpoints - Gestione impostazioni utente
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
import structlog

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....auth import get_current_user, User
from ....services.database import get_db
from ....services.zcs_api_service import get_zcs_service
from ....models.settings import (
    UserSettings,
    UserSettingsUpdate,
    UserSettingsResponse,
    DeviceInfo,
    ApiStatusResponse
)
from ....config.settings import get_settings

logger = structlog.get_logger()

router = APIRouter()


def get_default_settings(user_id: str) -> dict:
    """Return default settings for a new user"""
    return {
        "user_id": user_id,
        "system_name": "Il mio impianto",
        "language": "it",
        "timezone": "Europe/Rome",
        "currency": "EUR",
        "energy_price": 0.25,
        "sell_price": 0.10,
        "notification_email": None,
        "notify_critical_alarms": True,
        "notify_warnings": True,
        "notify_daily_report": False,
        "notify_weekly_report": True,
        "battery_low_threshold": 20,
        "battery_critical_threshold": 10,
        "realtime_interval": 60,
        "historical_interval": 15,
        "created_at": datetime.utcnow(),
        "updated_at": None
    }


@router.get("", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's settings"""
    try:
        # Query settings for current user
        result = await db.execute(
            select(UserSettings).where(UserSettings.user_id == current_user.id)
        )
        settings = result.scalar_one_or_none()
        
        if settings is None:
            # Return default settings (not yet saved)
            logger.info("No settings found, returning defaults", user_id=current_user.id)
            return UserSettingsResponse(**get_default_settings(current_user.id))
        
        logger.info("Retrieved user settings", user_id=current_user.id)
        return UserSettingsResponse.model_validate(settings)
        
    except Exception as e:
        logger.error("Error getting user settings", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Errore nel recupero impostazioni: {str(e)}")


@router.put("", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's settings (upsert)"""
    try:
        # Query existing settings
        result = await db.execute(
            select(UserSettings).where(UserSettings.user_id == current_user.id)
        )
        existing = result.scalar_one_or_none()
        
        if existing is None:
            # Create new settings
            new_settings = UserSettings(
                user_id=current_user.id,
                **settings_update.model_dump(exclude_unset=True)
            )
            db.add(new_settings)
            await db.commit()
            await db.refresh(new_settings)
            logger.info("Created user settings", user_id=current_user.id)
            return UserSettingsResponse.model_validate(new_settings)
        else:
            # Update existing settings
            update_data = settings_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(existing)
            logger.info("Updated user settings", user_id=current_user.id, fields=list(update_data.keys()))
            return UserSettingsResponse.model_validate(existing)
            
    except Exception as e:
        await db.rollback()
        logger.error("Error updating user settings", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Errore nel salvataggio impostazioni: {str(e)}")


@router.get("/devices", response_model=list[DeviceInfo])
async def get_settings_devices(
    current_user: User = Depends(get_current_user)
):
    """Get list of configured devices for settings page"""
    try:
        app_settings = get_settings()
        thing_keys = app_settings.device_thing_keys
        
        devices = []
        zcs_service = await get_zcs_service()
        
        for thing_key in thing_keys:
            # Try to get real-time status from ZCS
            status = "online"
            last_update = None
            
            try:
                realtime_data = await zcs_service.get_realtime_data(thing_key)
                if realtime_data and realtime_data.get("realtimeData"):
                    last_update = "Ora"
                    status = "online"
                else:
                    status = "offline"
            except Exception:
                status = "unknown"
            
            devices.append(DeviceInfo(
                thing_key=thing_key,
                name=f"Inverter ZCS {thing_key[-4:]}",
                device_type="Inverter Ibrido",
                status=status,
                last_update=last_update
            ))
        
        logger.info("Retrieved devices for settings", count=len(devices), user_id=current_user.id)
        return devices
        
    except Exception as e:
        logger.error("Error getting devices", error=str(e))
        raise HTTPException(status_code=500, detail=f"Errore nel recupero dispositivi: {str(e)}")


@router.get("/api-status", response_model=ApiStatusResponse)
async def get_api_status(
    current_user: User = Depends(get_current_user)
):
    """Get ZCS API connection status"""
    try:
        app_settings = get_settings()
        zcs_service = await get_zcs_service()
        
        # Test connection
        connected = False
        last_sync = None
        error = None
        
        try:
            thing_keys = app_settings.device_thing_keys
            if thing_keys:
                # Try to get data to verify connection
                data = await zcs_service.get_realtime_data(thing_keys[0])
                connected = data is not None
                if connected:
                    last_sync = datetime.utcnow().strftime("%H:%M:%S")
        except Exception as e:
            error = str(e)
            connected = False
        
        return ApiStatusResponse(
            endpoint="https://third.zcsazzurroportal.com:19003/",
            connected=connected,
            last_sync=last_sync,
            client_code_configured=bool(app_settings.ZCS_CLIENT_CODE),
            error=error
        )
        
    except Exception as e:
        logger.error("Error checking API status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Errore verifica stato API: {str(e)}")
