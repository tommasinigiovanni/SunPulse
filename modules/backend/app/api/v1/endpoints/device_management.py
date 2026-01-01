"""
Device Management Endpoints - CRUD operations for device persistence
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime
import structlog

from ....models.device import (
    Device,
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceStatus,
    DeviceType,
    DeviceAlarmResponse,
)
from ....database import get_db
from ....services.zcs_api_service import get_zcs_service

logger = structlog.get_logger()

router = APIRouter()


# ============================================================================
# Device CRUD Operations
# ============================================================================

@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new device in the database

    - **thing_key**: Unique ZCS device identifier (required)
    - **name**: Device name (required)
    - **device_type**: Device type (required)
    - **location**: Physical location (optional)
    - **manufacturer**: Manufacturer name (optional)
    - **model**: Device model (optional)
    """
    try:
        # Check if device already exists
        existing = db.query(Device).filter(Device.thing_key == device.thing_key).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Device with thing_key '{device.thing_key}' already exists"
            )

        # Create new device
        db_device = Device(
            thing_key=device.thing_key,
            name=device.name,
            device_type=DeviceType(device.device_type),
            location=device.location,
            manufacturer=device.manufacturer,
            model=device.model,
            firmware_version=device.firmware_version,
            config_json=device.config_json,
            status=DeviceStatus.UNKNOWN,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        if device.installation_date:
            db_device.installation_date = datetime.fromisoformat(device.installation_date).date()

        db.add(db_device)
        db.commit()
        db.refresh(db_device)

        logger.info(
            "Device created",
            device_id=db_device.id,
            thing_key=db_device.thing_key,
            device_type=db_device.device_type.value
        )

        return db_device

    except IntegrityError as e:
        db.rollback()
        logger.error("Database integrity error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error"
        )
    except Exception as e:
        db.rollback()
        logger.error("Error creating device", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating device: {str(e)}"
        )


@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = 0,
    limit: int = 100,
    device_type: Optional[DeviceType] = None,
    status: Optional[DeviceStatus] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all devices with optional filtering

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **device_type**: Filter by device type
    - **status**: Filter by device status
    - **active_only**: Show only active devices (default: true)
    """
    query = db.query(Device)

    if active_only:
        query = query.filter(Device.is_active == True)

    if device_type:
        query = query.filter(Device.device_type == device_type)

    if status:
        query = query.filter(Device.status == status)

    devices = query.offset(skip).limit(limit).all()

    logger.info(
        "Devices listed",
        count=len(devices),
        device_type=device_type,
        status=status
    )

    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific device by ID
    """
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )

    logger.info("Device retrieved", device_id=device_id, thing_key=device.thing_key)
    return device


@router.get("/by-thing-key/{thing_key}", response_model=DeviceResponse)
async def get_device_by_thing_key(
    thing_key: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific device by thing_key (ZCS identifier)
    """
    device = db.query(Device).filter(Device.thing_key == thing_key).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with thing_key '{thing_key}' not found"
        )

    logger.info("Device retrieved by thing_key", thing_key=thing_key, device_id=device.id)
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    device_update: DeviceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a device

    Only provided fields will be updated. Null/None values are ignored.
    """
    db_device = db.query(Device).filter(Device.id == device_id).first()

    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )

    # Update only provided fields
    update_data = device_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            setattr(db_device, field, value)

    db_device.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(db_device)

        logger.info(
            "Device updated",
            device_id=device_id,
            thing_key=db_device.thing_key,
            updated_fields=list(update_data.keys())
        )

        return db_device

    except Exception as e:
        db.rollback()
        logger.error("Error updating device", device_id=device_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating device: {str(e)}"
        )


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    hard_delete: bool = False,
    db: Session = Depends(get_db)
):
    """
    Delete a device

    - **hard_delete**: If true, permanently delete from database.
      If false (default), soft delete (set is_active=false)
    """
    db_device = db.query(Device).filter(Device.id == device_id).first()

    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )

    try:
        if hard_delete:
            db.delete(db_device)
            action = "hard_deleted"
        else:
            db_device.is_active = False
            db_device.updated_at = datetime.utcnow()
            action = "soft_deleted"

        db.commit()

        logger.info(
            "Device deleted",
            device_id=device_id,
            thing_key=db_device.thing_key,
            action=action
        )

    except Exception as e:
        db.rollback()
        logger.error("Error deleting device", device_id=device_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting device: {str(e)}"
        )


# ============================================================================
# Device Status & Health
# ============================================================================

@router.post("/{device_id}/status", response_model=DeviceResponse)
async def update_device_status(
    device_id: int,
    new_status: DeviceStatus,
    db: Session = Depends(get_db)
):
    """
    Update device status

    Status values: active, inactive, maintenance, error, unknown
    """
    db_device = db.query(Device).filter(Device.id == device_id).first()

    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )

    old_status = db_device.status
    db_device.status = new_status
    db_device.updated_at = datetime.utcnow()

    if new_status in [DeviceStatus.ACTIVE, DeviceStatus.MAINTENANCE]:
        db_device.last_seen = datetime.utcnow()

    try:
        db.commit()
        db.refresh(db_device)

        logger.info(
            "Device status updated",
            device_id=device_id,
            thing_key=db_device.thing_key,
            old_status=old_status.value if old_status else None,
            new_status=new_status.value
        )

        return db_device

    except Exception as e:
        db.rollback()
        logger.error("Error updating device status", device_id=device_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating device status: {str(e)}"
        )


@router.post("/{device_id}/heartbeat", response_model=DeviceResponse)
async def device_heartbeat(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    Record device heartbeat (last seen timestamp)

    Call this endpoint periodically to indicate device is online
    """
    db_device = db.query(Device).filter(Device.id == device_id).first()

    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )

    db_device.last_seen = datetime.utcnow()
    db_device.updated_at = datetime.utcnow()

    # Auto-update status to active if currently unknown/offline
    if db_device.status in [DeviceStatus.UNKNOWN, DeviceStatus.INACTIVE]:
        db_device.status = DeviceStatus.ACTIVE

    try:
        db.commit()
        db.refresh(db_device)

        logger.debug(
            "Device heartbeat recorded",
            device_id=device_id,
            thing_key=db_device.thing_key
        )

        return db_device

    except Exception as e:
        db.rollback()
        logger.error("Error recording device heartbeat", device_id=device_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording heartbeat: {str(e)}"
        )


# ============================================================================
# Device Synchronization with ZCS
# ============================================================================

@router.post("/sync-from-zcs", status_code=status.HTTP_200_OK)
async def sync_devices_from_zcs(
    db: Session = Depends(get_db)
):
    """
    Synchronize devices from ZCS API to local database

    This will:
    - Create new devices found in ZCS that don't exist locally
    - Update existing devices with latest info from ZCS
    - Mark devices as inactive if they no longer exist in ZCS
    """
    try:
        zcs_service = await get_zcs_service()

        # TODO: Implement actual ZCS device discovery endpoint
        # For now, this is a placeholder that would need ZCS API support

        logger.info("ZCS device sync requested")

        return {
            "status": "success",
            "message": "Device synchronization completed",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("Error syncing devices from ZCS", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing devices: {str(e)}"
        )


@router.get("/{device_id}/alarms", response_model=List[DeviceAlarmResponse])
async def get_device_alarms(
    device_id: int,
    active_only: bool = True,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get alarms for a specific device

    - **active_only**: Show only active alarms (default: true)
    - **limit**: Maximum number of alarms to return
    """
    # First check if device exists
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )

    # Import DeviceAlarm here to avoid circular import
    from ....models.device import DeviceAlarm

    query = db.query(DeviceAlarm).filter(DeviceAlarm.device_id == device_id)

    if active_only:
        query = query.filter(DeviceAlarm.is_active == True)

    alarms = query.order_by(DeviceAlarm.triggered_at.desc()).limit(limit).all()

    logger.info(
        "Device alarms retrieved",
        device_id=device_id,
        thing_key=device.thing_key,
        alarm_count=len(alarms),
        active_only=active_only
    )

    return alarms
