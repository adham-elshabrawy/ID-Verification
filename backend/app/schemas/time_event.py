from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class TimeEventCreate(BaseModel):
    employee_id: UUID
    event_type: str  # 'IN' or 'OUT'
    method: str  # 'FACE' or 'PIN'
    event_time: Optional[datetime] = None  # If None, use current time


class TimeEventUpdate(BaseModel):
    event_type: Optional[str] = None
    event_time: Optional[datetime] = None
    is_valid: Optional[bool] = None


class TimeEventResponse(BaseModel):
    id: UUID
    employee_id: UUID
    device_id: UUID
    location_id: UUID
    event_type: str
    event_time: datetime
    method: str
    is_valid: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ClockedInEmployee(BaseModel):
    employee_id: str
    name: str
    clock_in_time: datetime
    device_id: UUID
    device_name: Optional[str] = None

