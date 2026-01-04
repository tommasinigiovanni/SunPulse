"""
Building Service for SunPulse

Manages CRUD operations for buildings and related entities.
"""
import structlog
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.building import (
    Building, UserBuilding, BuildingDevice, BuildingWeather,
    BuildingCreate, BuildingUpdate, BuildingResponse,
    UserBuildingRole, BuildingDeviceCreate, BuildingDeviceResponse,
    BuildingMemberResponse
)
from app.services.weather_service import get_weather_service

logger = structlog.get_logger()


class BuildingService:
    """Service for managing buildings"""
    
    # --- Building CRUD ---
    
    def create_building(
        self, 
        db: Session, 
        user_id: str,
        building_data: BuildingCreate
    ) -> Building:
        """
        Create a new building and assign the creator as owner
        
        Args:
            db: Database session
            user_id: Auth0 user ID of creator
            building_data: Building creation data
            
        Returns:
            Created building
        """
        # Create building
        building = Building(
            name=building_data.name,
            address=building_data.address,
            place_id=building_data.place_id,
            address_components=building_data.address_components,
            latitude=building_data.latitude,
            longitude=building_data.longitude,
            timezone=building_data.timezone or "Europe/Rome",
            created_by=user_id
        )
        
        db.add(building)
        db.flush()  # Get the building ID
        
        # Create user-building relationship with owner role
        user_building = UserBuilding(
            user_id=user_id,
            building_id=building.id,
            role=UserBuildingRole.OWNER.value,
            invitation_accepted=True
        )
        
        db.add(user_building)
        db.commit()
        db.refresh(building)
        
        logger.info(f"Created building {building.id} for user {user_id}")
        
        return building
    
    def get_building(
        self, 
        db: Session, 
        building_id: int,
        user_id: Optional[str] = None
    ) -> Optional[Building]:
        """
        Get a building by ID
        
        Args:
            db: Database session
            building_id: Building ID
            user_id: Optional user ID to verify access
            
        Returns:
            Building or None
        """
        query = db.query(Building).filter(Building.id == building_id)
        
        # If user_id provided, verify access
        if user_id:
            query = query.join(UserBuilding).filter(
                UserBuilding.user_id == user_id
            )
        
        return query.first()
    
    def get_user_buildings(
        self, 
        db: Session, 
        user_id: str
    ) -> List[BuildingResponse]:
        """
        Get all buildings accessible by a user
        
        Args:
            db: Database session
            user_id: Auth0 user ID
            
        Returns:
            List of buildings with metadata
        """
        # Query buildings with device count and latest weather
        buildings_query = db.query(
            Building,
            func.count(BuildingDevice.id).label('device_count'),
            UserBuilding.role
        ).join(
            UserBuilding, UserBuilding.building_id == Building.id
        ).outerjoin(
            BuildingDevice, BuildingDevice.building_id == Building.id
        ).filter(
            UserBuilding.user_id == user_id
        ).group_by(
            Building.id, UserBuilding.role
        ).order_by(
            Building.created_at.desc()
        )
        
        results = buildings_query.all()
        
        buildings_response = []
        weather_service = get_weather_service()
        
        for building, device_count, role in results:
            # Get latest weather
            latest_weather = weather_service.get_latest_weather(db, building.id)
            
            buildings_response.append(BuildingResponse(
                id=building.id,
                name=building.name,
                address=building.address,
                place_id=building.place_id,
                latitude=building.latitude,
                longitude=building.longitude,
                timezone=building.timezone,
                created_at=building.created_at,
                updated_at=building.updated_at,
                device_count=device_count,
                current_temperature=latest_weather.temperature if latest_weather else None,
                weather_condition=latest_weather.weather_condition if latest_weather else None
            ))
        
        return buildings_response
    
    def update_building(
        self, 
        db: Session, 
        building_id: int,
        user_id: str,
        update_data: BuildingUpdate
    ) -> Optional[Building]:
        """
        Update a building
        
        Args:
            db: Database session
            building_id: Building ID
            user_id: User ID (must be admin or owner)
            update_data: Update data
            
        Returns:
            Updated building or None
        """
        # Check access (admin or owner required)
        if not self.check_access(db, user_id, building_id, min_role="admin"):
            logger.warning(f"User {user_id} not authorized to update building {building_id}")
            return None
        
        building = db.query(Building).filter(Building.id == building_id).first()
        if not building:
            return None
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(building, field, value)
        
        building.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(building)
        
        logger.info(f"Updated building {building_id}")
        
        return building
    
    def delete_building(
        self, 
        db: Session, 
        building_id: int,
        user_id: str
    ) -> bool:
        """
        Delete a building (owner only)
        
        Args:
            db: Database session
            building_id: Building ID
            user_id: User ID (must be owner)
            
        Returns:
            True if deleted
        """
        # Only owner can delete
        if not self.check_access(db, user_id, building_id, min_role="owner"):
            logger.warning(f"User {user_id} not authorized to delete building {building_id}")
            return False
        
        building = db.query(Building).filter(Building.id == building_id).first()
        if not building:
            return False
        
        db.delete(building)
        db.commit()
        
        logger.info(f"Deleted building {building_id}")
        
        return True
    
    # --- Access Control ---
    
    def check_access(
        self, 
        db: Session, 
        user_id: str, 
        building_id: int,
        min_role: str = "viewer"
    ) -> bool:
        """
        Check if user has access to building with minimum role
        
        Args:
            db: Database session
            user_id: User ID
            building_id: Building ID
            min_role: Minimum required role
            
        Returns:
            True if authorized
        """
        user_building = db.query(UserBuilding).filter(
            UserBuilding.user_id == user_id,
            UserBuilding.building_id == building_id
        ).first()
        
        if not user_building:
            return False
        
        # Role hierarchy
        role_levels = {
            "viewer": 1,
            "member": 2,
            "admin": 3,
            "owner": 4
        }
        
        user_level = role_levels.get(user_building.role, 0)
        min_level = role_levels.get(min_role, 0)
        
        return user_level >= min_level
    
    def get_user_role(
        self, 
        db: Session, 
        user_id: str, 
        building_id: int
    ) -> Optional[str]:
        """Get user's role for a building"""
        user_building = db.query(UserBuilding).filter(
            UserBuilding.user_id == user_id,
            UserBuilding.building_id == building_id
        ).first()
        
        return user_building.role if user_building else None
    
    # --- Members Management ---
    
    def get_members(
        self, 
        db: Session, 
        building_id: int
    ) -> List[BuildingMemberResponse]:
        """Get all members of a building"""
        members = db.query(UserBuilding).filter(
            UserBuilding.building_id == building_id
        ).order_by(
            UserBuilding.joined_at
        ).all()
        
        return [
            BuildingMemberResponse(
                user_id=m.user_id,
                email=m.invitation_email,
                name=None,  # Would need to fetch from Auth0
                role=m.role,
                joined_at=m.joined_at,
                invitation_accepted=m.invitation_accepted
            )
            for m in members
        ]
    
    def add_member(
        self, 
        db: Session, 
        building_id: int,
        inviter_id: str,
        email: str,
        role: str = "member",
        user_id: Optional[str] = None
    ) -> Optional[UserBuilding]:
        """
        Add a member to a building
        
        Args:
            db: Database session
            building_id: Building ID
            inviter_id: User ID of inviter
            email: Email of invitee
            role: Role to assign
            user_id: Optional known user ID
            
        Returns:
            Created UserBuilding or None
        """
        import secrets
        
        # Check if inviter has permission (admin or owner)
        if not self.check_access(db, inviter_id, building_id, min_role="admin"):
            return None
        
        # Generate invitation token
        invitation_token = secrets.token_urlsafe(32)
        
        user_building = UserBuilding(
            user_id=user_id or f"pending_{invitation_token[:8]}",
            building_id=building_id,
            role=role,
            invited_by=inviter_id,
            invitation_email=email,
            invitation_token=invitation_token,
            invitation_accepted=user_id is not None
        )
        
        db.add(user_building)
        db.commit()
        db.refresh(user_building)
        
        logger.info(f"Added member {email} to building {building_id} with role {role}")
        
        return user_building
    
    def update_member_role(
        self, 
        db: Session, 
        building_id: int,
        admin_id: str,
        target_user_id: str,
        new_role: str
    ) -> bool:
        """Update a member's role"""
        # Check admin permission
        if not self.check_access(db, admin_id, building_id, min_role="admin"):
            return False
        
        # Cannot change owner role unless you're the owner
        target_member = db.query(UserBuilding).filter(
            UserBuilding.user_id == target_user_id,
            UserBuilding.building_id == building_id
        ).first()
        
        if not target_member:
            return False
        
        if target_member.role == "owner" and not self.check_access(db, admin_id, building_id, min_role="owner"):
            return False
        
        target_member.role = new_role
        db.commit()
        
        logger.info(f"Updated role for user {target_user_id} in building {building_id} to {new_role}")
        
        return True
    
    def remove_member(
        self, 
        db: Session, 
        building_id: int,
        admin_id: str,
        target_user_id: str
    ) -> bool:
        """Remove a member from a building"""
        # Check admin permission
        if not self.check_access(db, admin_id, building_id, min_role="admin"):
            return False
        
        # Cannot remove owner
        target_member = db.query(UserBuilding).filter(
            UserBuilding.user_id == target_user_id,
            UserBuilding.building_id == building_id
        ).first()
        
        if not target_member or target_member.role == "owner":
            return False
        
        db.delete(target_member)
        db.commit()
        
        logger.info(f"Removed user {target_user_id} from building {building_id}")
        
        return True
    
    # --- Device Management ---
    
    def get_devices(
        self, 
        db: Session, 
        building_id: int
    ) -> List[BuildingDeviceResponse]:
        """Get all devices for a building"""
        devices = db.query(BuildingDevice).filter(
            BuildingDevice.building_id == building_id
        ).order_by(
            BuildingDevice.created_at
        ).all()
        
        return [
            BuildingDeviceResponse(
                id=d.id,
                building_id=d.building_id,
                thing_key=d.thing_key,
                name=d.name,
                device_type=d.device_type,
                status=d.status,
                last_seen=d.last_seen,
                created_at=d.created_at
            )
            for d in devices
        ]
    
    def add_device(
        self, 
        db: Session, 
        building_id: int,
        user_id: str,
        device_data: BuildingDeviceCreate
    ) -> Optional[BuildingDevice]:
        """Add a device to a building"""
        # Check permission (member or above)
        if not self.check_access(db, user_id, building_id, min_role="member"):
            return None
        
        # Check if device already exists in this building
        existing = db.query(BuildingDevice).filter(
            BuildingDevice.building_id == building_id,
            BuildingDevice.thing_key == device_data.thing_key
        ).first()
        
        if existing:
            logger.warning(f"Device {device_data.thing_key} already exists in building {building_id}")
            return existing
        
        device = BuildingDevice(
            building_id=building_id,
            thing_key=device_data.thing_key,
            name=device_data.name or f"Device {device_data.thing_key[-6:]}",
            device_type=device_data.device_type or "inverter"
        )
        
        db.add(device)
        db.commit()
        db.refresh(device)
        
        logger.info(f"Added device {device_data.thing_key} to building {building_id}")
        
        return device
    
    def remove_device(
        self, 
        db: Session, 
        building_id: int,
        device_id: int,
        user_id: str
    ) -> bool:
        """Remove a device from a building"""
        # Check permission (admin or above)
        if not self.check_access(db, user_id, building_id, min_role="admin"):
            return False
        
        device = db.query(BuildingDevice).filter(
            BuildingDevice.id == device_id,
            BuildingDevice.building_id == building_id
        ).first()
        
        if not device:
            return False
        
        db.delete(device)
        db.commit()
        
        logger.info(f"Removed device {device_id} from building {building_id}")
        
        return True
    
    def update_device_status(
        self, 
        db: Session, 
        thing_key: str,
        status: str,
        last_seen: Optional[datetime] = None
    ) -> bool:
        """Update device status (called by data collector)"""
        device = db.query(BuildingDevice).filter(
            BuildingDevice.thing_key == thing_key
        ).first()
        
        if not device:
            return False
        
        device.status = status
        device.last_seen = last_seen or datetime.now(timezone.utc)
        db.commit()
        
        return True
    
    # --- Helpers ---
    
    def get_building_thing_keys(
        self, 
        db: Session, 
        building_id: int
    ) -> List[str]:
        """Get all thing keys for a building"""
        devices = db.query(BuildingDevice.thing_key).filter(
            BuildingDevice.building_id == building_id
        ).all()
        
        return [d.thing_key for d in devices]
    
    def get_user_thing_keys(
        self, 
        db: Session, 
        user_id: str
    ) -> List[str]:
        """Get all thing keys for all buildings a user has access to"""
        thing_keys = db.query(BuildingDevice.thing_key).join(
            UserBuilding, UserBuilding.building_id == BuildingDevice.building_id
        ).filter(
            UserBuilding.user_id == user_id
        ).all()
        
        return [tk.thing_key for tk in thing_keys]


# Singleton instance
_building_service: Optional[BuildingService] = None


def get_building_service() -> BuildingService:
    """Get or create the building service singleton"""
    global _building_service
    if _building_service is None:
        _building_service = BuildingService()
    return _building_service
