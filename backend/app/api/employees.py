from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from uuid import UUID
import bcrypt
import numpy as np
from app.database import get_db
from app.models.employee import Employee
from app.models.location import Location
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeStateResponse
from app.security import get_current_device
from app.services.face_service import face_service
from app.services.clock_logic import clock_logic_service

router = APIRouter(prefix="/api/employees", tags=["employees"])


def hash_pin(pin: str) -> str:
    """Hash a PIN using bcrypt"""
    return bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """List all employees at device location (admin)"""
    employees = db.query(Employee).filter(
        Employee.location_id == device.location_id
    ).order_by(Employee.name).all()
    
    return [
        EmployeeResponse(
            id=e.id,
            location_id=e.location_id,
            employee_id=e.employee_id,
            name=e.name,
            is_active=e.is_active,
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in employees
    ]


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Create a new employee (admin)"""
    # Verify location
    if employee_data.location_id != device.location_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create employee for different location"
        )
    
    # Hash PIN
    pin_hash = hash_pin(employee_data.pin)
    
    employee = Employee(
        location_id=employee_data.location_id,
        employee_id=employee_data.employee_id,
        name=employee_data.name,
        pin_hash=pin_hash,
        is_active=True
    )
    
    try:
        db.add(employee)
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists at this location"
        )
    
    return EmployeeResponse(
        id=employee.id,
        location_id=employee.location_id,
        employee_id=employee.employee_id,
        name=employee.name,
        is_active=employee.is_active,
        created_at=employee.created_at,
        updated_at=employee.updated_at
    )


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    employee_update: EmployeeUpdate,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Update an employee (admin)"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.location_id == device.location_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    if employee_update.name is not None:
        employee.name = employee_update.name
    if employee_update.pin is not None:
        employee.pin_hash = hash_pin(employee_update.pin)
    if employee_update.is_active is not None:
        employee.is_active = employee_update.is_active
    
    db.commit()
    db.refresh(employee)
    
    return EmployeeResponse(
        id=employee.id,
        location_id=employee.location_id,
        employee_id=employee.employee_id,
        name=employee.name,
        is_active=employee.is_active,
        created_at=employee.created_at,
        updated_at=employee.updated_at
    )


@router.post("/{employee_id}/deactivate", response_model=EmployeeResponse)
async def deactivate_employee(
    employee_id: UUID,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Deactivate an employee (admin)"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.location_id == device.location_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    employee.is_active = False
    db.commit()
    db.refresh(employee)
    
    return EmployeeResponse(
        id=employee.id,
        location_id=employee.location_id,
        employee_id=employee.employee_id,
        name=employee.name,
        is_active=employee.is_active,
        created_at=employee.created_at,
        updated_at=employee.updated_at
    )


@router.get("/{employee_id}/state", response_model=EmployeeStateResponse)
async def get_employee_state(
    employee_id: UUID,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Get current clock state for an employee"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.location_id == device.location_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    state, last_event = clock_logic_service.get_employee_state(
        db,
        employee.employee_id,
        str(employee.location_id)
    )
    
    return EmployeeStateResponse(
        employee_id=employee.employee_id,
        name=employee.name,
        state=state,
        last_event_time=last_event.event_time if last_event else None,
        last_event_type=last_event.event_type if last_event else None
    )

