"""
Onboarding Service for SunPulse

Manages the user onboarding wizard flow.
"""
import structlog
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.building import (
    UserOnboarding, OnboardingStatus, Building, BuildingDevice,
    OnboardingStatusResponse, OnboardingDeviceValidationResponse,
    BuildingCreate
)
from app.services.building_service import get_building_service
from app.services.zcs_api_service import get_zcs_service

logger = structlog.get_logger()


class OnboardingService:
    """Service for managing user onboarding wizard"""
    
    TOTAL_STEPS = 5
    
    def get_or_create_onboarding(
        self, 
        db: Session, 
        user_id: str
    ) -> UserOnboarding:
        """
        Get or create onboarding record for user
        
        Args:
            db: Database session
            user_id: Auth0 user ID
            
        Returns:
            UserOnboarding record
        """
        onboarding = db.query(UserOnboarding).filter(
            UserOnboarding.user_id == user_id
        ).first()
        
        if not onboarding:
            onboarding = UserOnboarding(
                user_id=user_id,
                current_step=1,
                status=OnboardingStatus.NOT_STARTED.value,
                step_data={}
            )
            db.add(onboarding)
            db.commit()
            db.refresh(onboarding)
            logger.info(f"Created onboarding record for user {user_id}")
        
        return onboarding
    
    def get_status(
        self, 
        db: Session, 
        user_id: str
    ) -> OnboardingStatusResponse:
        """
        Get onboarding status for user
        
        Args:
            db: Database session
            user_id: Auth0 user ID
            
        Returns:
            Onboarding status
        """
        onboarding = self.get_or_create_onboarding(db, user_id)
        
        return OnboardingStatusResponse(
            user_id=user_id,
            current_step=onboarding.current_step,
            status=onboarding.status,
            building_id=onboarding.building_id,
            step_data=onboarding.step_data,
            started_at=onboarding.started_at,
            completed_at=onboarding.completed_at
        )
    
    def is_completed(
        self, 
        db: Session, 
        user_id: str
    ) -> bool:
        """Check if user has completed or skipped onboarding"""
        onboarding = db.query(UserOnboarding).filter(
            UserOnboarding.user_id == user_id
        ).first()
        
        if not onboarding:
            # Check if user has any buildings (invited to existing)
            building_service = get_building_service()
            buildings = building_service.get_user_buildings(db, user_id)
            return len(buildings) > 0
        
        return onboarding.status in [
            OnboardingStatus.COMPLETED.value,
            OnboardingStatus.SKIPPED.value
        ]
    
    def start_wizard(
        self, 
        db: Session, 
        user_id: str
    ) -> OnboardingStatusResponse:
        """
        Start the onboarding wizard
        
        Args:
            db: Database session
            user_id: Auth0 user ID
            
        Returns:
            Updated onboarding status
        """
        onboarding = self.get_or_create_onboarding(db, user_id)
        
        onboarding.status = OnboardingStatus.IN_PROGRESS.value
        onboarding.started_at = datetime.now(timezone.utc)
        onboarding.current_step = 1
        
        db.commit()
        db.refresh(onboarding)
        
        logger.info(f"Started onboarding wizard for user {user_id}")
        
        return self.get_status(db, user_id)
    
    def save_step(
        self, 
        db: Session, 
        user_id: str,
        step: int,
        step_data: Dict[str, Any]
    ) -> OnboardingStatusResponse:
        """
        Save data for a wizard step and advance to next
        
        Args:
            db: Database session
            user_id: Auth0 user ID
            step: Current step number (1-5)
            step_data: Data from the step form
            
        Returns:
            Updated onboarding status
        """
        onboarding = self.get_or_create_onboarding(db, user_id)
        
        # Validate step
        if step < 1 or step > self.TOTAL_STEPS:
            raise ValueError(f"Invalid step: {step}")
        
        # Store step data
        current_data = onboarding.step_data or {}
        current_data[f"step_{step}"] = step_data
        onboarding.step_data = current_data
        
        # Update status
        if onboarding.status == OnboardingStatus.NOT_STARTED.value:
            onboarding.status = OnboardingStatus.IN_PROGRESS.value
            onboarding.started_at = datetime.now(timezone.utc)
        
        # Process step-specific actions
        if step == 2:  # Building step
            self._process_building_step(db, user_id, step_data, onboarding)
        elif step == 3:  # Devices step
            self._process_devices_step(db, user_id, step_data, onboarding)
        elif step == 4:  # Notifications step (optional)
            self._process_notifications_step(db, user_id, step_data)
        
        # Advance to next step
        if step < self.TOTAL_STEPS:
            onboarding.current_step = step + 1
        
        db.commit()
        db.refresh(onboarding)
        
        logger.info(f"Saved step {step} for user {user_id}")
        
        return self.get_status(db, user_id)
    
    def _process_building_step(
        self, 
        db: Session, 
        user_id: str,
        step_data: Dict[str, Any],
        onboarding: UserOnboarding
    ):
        """Process building creation from step 2"""
        building_service = get_building_service()
        
        # Create building
        building_data = BuildingCreate(
            name=step_data.get("name", "Il mio edificio"),
            address=step_data.get("address", ""),
            place_id=step_data.get("place_id"),
            address_components=step_data.get("address_components"),
            latitude=step_data.get("latitude"),
            longitude=step_data.get("longitude"),
            timezone=step_data.get("timezone", "Europe/Rome")
        )
        
        building = building_service.create_building(db, user_id, building_data)
        onboarding.building_id = building.id
        
        logger.info(f"Created building {building.id} during onboarding for user {user_id}")
    
    def _process_devices_step(
        self, 
        db: Session, 
        user_id: str,
        step_data: Dict[str, Any],
        onboarding: UserOnboarding
    ):
        """Process device additions from step 3"""
        if not onboarding.building_id:
            logger.warning("No building found during device step")
            return
        
        building_service = get_building_service()
        devices = step_data.get("devices", [])
        
        for device_data in devices:
            from app.models.building import BuildingDeviceCreate
            device_create = BuildingDeviceCreate(
                thing_key=device_data.get("thing_key"),
                name=device_data.get("name"),
                device_type=device_data.get("device_type", "inverter")
            )
            building_service.add_device(db, onboarding.building_id, user_id, device_create)
        
        logger.info(f"Added {len(devices)} devices during onboarding for user {user_id}")
    
    def _process_notifications_step(
        self, 
        db: Session, 
        user_id: str,
        step_data: Dict[str, Any]
    ):
        """Process notification settings from step 4"""
        from app.models.settings import UserSettings
        
        # Update user settings with notification preferences
        settings = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        
        if settings:
            settings.notification_email = step_data.get("email")
            settings.notify_critical_alarms = step_data.get("notify_critical_alarms", True)
            settings.notify_warnings = step_data.get("notify_warnings", True)
            settings.notify_daily_report = step_data.get("notify_daily_report", False)
            settings.notify_weekly_report = step_data.get("notify_weekly_report", True)
        else:
            # Create new settings
            settings = UserSettings(
                user_id=user_id,
                notification_email=step_data.get("email"),
                notify_critical_alarms=step_data.get("notify_critical_alarms", True),
                notify_warnings=step_data.get("notify_warnings", True),
                notify_daily_report=step_data.get("notify_daily_report", False),
                notify_weekly_report=step_data.get("notify_weekly_report", True)
            )
            db.add(settings)
        
        logger.info(f"Updated notification settings during onboarding for user {user_id}")
    
    def complete_wizard(
        self, 
        db: Session, 
        user_id: str
    ) -> OnboardingStatusResponse:
        """
        Mark the onboarding wizard as completed
        
        Args:
            db: Database session
            user_id: Auth0 user ID
            
        Returns:
            Updated onboarding status
        """
        onboarding = self.get_or_create_onboarding(db, user_id)
        
        onboarding.status = OnboardingStatus.COMPLETED.value
        onboarding.completed_at = datetime.now(timezone.utc)
        onboarding.current_step = self.TOTAL_STEPS
        
        db.commit()
        db.refresh(onboarding)
        
        logger.info(f"Completed onboarding wizard for user {user_id}")
        
        return self.get_status(db, user_id)
    
    def skip_wizard(
        self, 
        db: Session, 
        user_id: str
    ) -> OnboardingStatusResponse:
        """
        Skip the onboarding wizard (only if user has buildings)
        
        Args:
            db: Database session
            user_id: Auth0 user ID
            
        Returns:
            Updated onboarding status
            
        Raises:
            ValueError: If user has no buildings
        """
        # Check if user has any buildings
        building_service = get_building_service()
        buildings = building_service.get_user_buildings(db, user_id)
        
        if not buildings:
            raise ValueError("Cannot skip onboarding without buildings")
        
        onboarding = self.get_or_create_onboarding(db, user_id)
        
        onboarding.status = OnboardingStatus.SKIPPED.value
        onboarding.completed_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(onboarding)
        
        logger.info(f"Skipped onboarding wizard for user {user_id}")
        
        return self.get_status(db, user_id)
    
    async def validate_device(
        self, 
        thing_key: str
    ) -> OnboardingDeviceValidationResponse:
        """
        Validate a device thing_key against ZCS API
        
        Args:
            thing_key: ZCS device identifier
            
        Returns:
            Validation result with device info if valid
        """
        try:
            zcs_service = get_zcs_service()
            
            # Try to fetch realtime data to verify device exists
            data = await zcs_service.get_realtime_data(thing_key)
            
            if data and data.get("realtimeData"):
                realtime = data["realtimeData"]
                
                return OnboardingDeviceValidationResponse(
                    thing_key=thing_key,
                    valid=True,
                    device_info={
                        "status": "online" if realtime.get("thingFind") else "offline",
                        "last_update": realtime.get("lastUpdate"),
                        "battery_soc": realtime.get("batterySoC"),
                        "power_generating": realtime.get("powerGenerating")
                    },
                    error=None
                )
            else:
                return OnboardingDeviceValidationResponse(
                    thing_key=thing_key,
                    valid=False,
                    device_info=None,
                    error="Dispositivo non trovato o non raggiungibile"
                )
                
        except Exception as e:
            logger.error(f"Error validating device {thing_key}: {e}")
            return OnboardingDeviceValidationResponse(
                thing_key=thing_key,
                valid=False,
                device_info=None,
                error=f"Errore nella validazione: {str(e)}"
            )


# Singleton instance
_onboarding_service: Optional[OnboardingService] = None


def get_onboarding_service() -> OnboardingService:
    """Get or create the onboarding service singleton"""
    global _onboarding_service
    if _onboarding_service is None:
        _onboarding_service = OnboardingService()
    return _onboarding_service
