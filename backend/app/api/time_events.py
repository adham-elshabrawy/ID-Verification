from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models.time_event import TimeEvent
from app.models.employee import Employee
from app.models.device import Device
from app.schemas.time_event import TimeEventCreate, TimeEventUpdate, TimeEventResponse, ClockedInEmployee
from app.security import get_current_device
from app.services.clock_logic import clock_logic_service

router = APIRouter(prefix="/api/time-events", tags=["time-events"])


@router.post("", response_model=TimeEventResponse, status_code=status.HTTP_201_CREATED)
async def create_time_event(
    event_data: TimeEventCreate,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Create a new time event (clock in/out)"""
    # Get employee
    employee = db.query(Employee).filter(Employee.id == event_data.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Validate employee belongs to device location
    if employee.location_id != device.location_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee does not belong to device location"
        )
    
    # Validate clock state transition
    can_proceed, error_msg = clock_logic_service.validate_event(
        db,
        employee.employee_id,
        str(employee.location_id),
        event_data.event_type
    )
    
    if not can_proceed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Create event
    event_time = event_data.event_time or datetime.utcnow()
    
    time_event = TimeEvent(
        employee_id=employee.id,
        device_id=device.id,
        location_id=device.location_id,
        event_type=event_data.event_type,
        event_time=event_time,
        method=event_data.method,
        is_valid=True
    )
    
    db.add(time_event)
    db.commit()
    db.refresh(time_event)
    
    return TimeEventResponse(
        id=time_event.id,
        employee_id=time_event.employee_id,
        device_id=time_event.device_id,
        location_id=time_event.location_id,
        event_type=time_event.event_type,
        event_time=time_event.event_time,
        method=time_event.method,
        is_valid=time_event.is_valid,
        created_at=time_event.created_at
    )


@router.get("", response_model=List[TimeEventResponse])
async def list_time_events(
    location_id: Optional[UUID] = Query(None),
    employee_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """
    List time events (admin view)
    Filtered by device location by default
    """
    query = db.query(TimeEvent).filter(TimeEvent.location_id == device.location_id)
    
    if employee_id:
        query = query.filter(TimeEvent.employee_id == employee_id)
    
    if start_date:
        query = query.filter(TimeEvent.event_time >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        query = query.filter(TimeEvent.event_time <= datetime.combine(end_date, datetime.max.time()))
    
    events = query.order_by(desc(TimeEvent.event_time)).limit(1000).all()
    
    return [
        TimeEventResponse(
            id=e.id,
            employee_id=e.employee_id,
            device_id=e.device_id,
            location_id=e.location_id,
            event_type=e.event_type,
            event_time=e.event_time,
            method=e.method,
            is_valid=e.is_valid,
            created_at=e.created_at
        )
        for e in events
    ]


@router.put("/{event_id}", response_model=TimeEventResponse)
async def update_time_event(
    event_id: UUID,
    event_update: TimeEventUpdate,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Update a time event (admin only)"""
    time_event = db.query(TimeEvent).filter(
        TimeEvent.id == event_id,
        TimeEvent.location_id == device.location_id
    ).first()
    
    if not time_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time event not found"
        )
    
    if event_update.event_type is not None:
        time_event.event_type = event_update.event_type
    if event_update.event_time is not None:
        time_event.event_time = event_update.event_time
    if event_update.is_valid is not None:
        time_event.is_valid = event_update.is_valid
    
    db.commit()
    db.refresh(time_event)
    
    return TimeEventResponse(
        id=time_event.id,
        employee_id=time_event.employee_id,
        device_id=time_event.device_id,
        location_id=time_event.location_id,
        event_type=time_event.event_type,
        event_time=time_event.event_time,
        method=time_event.method,
        is_valid=time_event.is_valid,
        created_at=time_event.created_at
    )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def invalidate_time_event(
    event_id: UUID,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Mark a time event as invalid (admin only)"""
    time_event = db.query(TimeEvent).filter(
        TimeEvent.id == event_id,
        TimeEvent.location_id == device.location_id
    ).first()
    
    if not time_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time event not found"
        )
    
    time_event.is_valid = False
    db.commit()
    
    return None


@router.get("/clocked-in", response_model=List[ClockedInEmployee])
async def get_clocked_in_employees(
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Get list of currently clocked in employees"""
    # Get all employees at location
    employees = db.query(Employee).filter(
        Employee.location_id == device.location_id,
        Employee.is_active == True
    ).all()
    
    clocked_in = []
    for employee in employees:
        state, last_event = clock_logic_service.get_employee_state(
            db,
            employee.employee_id,
            str(employee.location_id)
        )
        
        if state == "CLOCKED_IN" and last_event:
            device_info = db.query(Device).filter(Device.id == last_event.device_id).first()
            clocked_in.append(ClockedInEmployee(
                employee_id=employee.employee_id,
                name=employee.name,
                clock_in_time=last_event.event_time,
                device_id=last_event.device_id,
                device_name=device_info.name if device_info else None
            ))
    
    return clocked_in

