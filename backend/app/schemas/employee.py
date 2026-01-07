from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    pin: str


class EmployeeCreate(EmployeeBase):
    location_id: UUID


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    pin: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeResponse(BaseModel):
    id: UUID
    location_id: UUID
    employee_id: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeStateResponse(BaseModel):
    employee_id: str
    name: str
    state: str  # "CLOCKED_IN" or "CLOCKED_OUT"
    last_event_time: Optional[datetime] = None
    last_event_type: Optional[str] = None

