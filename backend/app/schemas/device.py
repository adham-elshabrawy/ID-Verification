from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class DeviceRegister(BaseModel):
    device_id: str
    location_name: str
    name: Optional[str] = None


class DeviceRegisterResponse(BaseModel):
    device_id: str
    api_key: str
    location_id: UUID
    location_name: str


class DeviceResponse(BaseModel):
    id: UUID
    device_id: str
    location_id: UUID
    name: Optional[str] = None
    registered_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True

