from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.database import get_db
from app.models.device import Device
from app.models.location import Location
from app.schemas.device import DeviceRegister, DeviceRegisterResponse, DeviceResponse
from app.security import generate_api_key, hash_api_key, get_current_device

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.post("/register", response_model=DeviceRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    device_data: DeviceRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new device
    Creates location if it doesn't exist
    Returns API key for device authentication
    """
    # Find or create location
    location = db.query(Location).filter(Location.name == device_data.location_name).first()
    if not location:
        # Create new location with default values
        location = Location(
            name=device_data.location_name,
            manager_email="",  # Set via admin later
            export_time=datetime.now().time(),  # Default to current time
            timezone="America/Toronto"
        )
        db.add(location)
        db.flush()
    
    # Check if device already exists
    existing_device = db.query(Device).filter(Device.device_id == device_data.device_id).first()
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device already registered"
        )
    
    # Generate API key
    api_key = generate_api_key()
    api_key_hash = hash_api_key(api_key)
    
    # Create device
    device = Device(
        device_id=device_data.device_id,
        location_id=location.id,
        api_key=api_key_hash,
        name=device_data.name,
        registered_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow()
    )
    
    try:
        db.add(device)
        db.commit()
        db.refresh(device)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device registration failed"
        )
    
    return DeviceRegisterResponse(
        device_id=device.device_id,
        api_key=api_key,  # Return plaintext key (only time it's returned)
        location_id=location.id,
        location_name=location.name
    )


@router.get("/me", response_model=DeviceResponse)
async def get_device_info(
    device: Device = Depends(get_current_device)
):
    """Get current device information"""
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        location_id=device.location_id,
        name=device.name,
        registered_at=device.registered_at,
        last_seen_at=device.last_seen_at
    )


@router.post("/ping")
async def ping_device(
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Update device last_seen_at timestamp"""
    device.last_seen_at = datetime.utcnow()
    db.commit()
    return {"status": "ok"}

