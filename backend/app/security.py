from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
import bcrypt
import secrets
from app.database import get_db
from app.models.device import Device

api_key_header = APIKeyHeader(name="X-Device-API-Key", auto_error=False)


def generate_api_key() -> str:
    """Generate a random API key"""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key using bcrypt"""
    return bcrypt.hashpw(api_key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_api_key(api_key: str, hashed: str) -> bool:
    """Verify an API key against its hash"""
    return bcrypt.checkpw(api_key.encode('utf-8'), hashed.encode('utf-8'))


async def get_current_device(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Device:
    """
    Dependency to get the current authenticated device
    
    Raises HTTPException if authentication fails
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # Find device by comparing API key hash
    devices = db.query(Device).all()
    for device in devices:
        if verify_api_key(api_key, device.api_key):
            # Update last_seen_at
            from datetime import datetime
            device.last_seen_at = datetime.utcnow()
            db.commit()
            return device
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )

