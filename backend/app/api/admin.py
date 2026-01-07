from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List
from app.database import get_db
from app.models.device import Device
from app.models.location import Location
from app.security import get_current_device
from app.services.export_service import export_service
from app.services.clock_logic import clock_logic_service
from app.models.employee import Employee
from app.models.time_event import TimeEvent
from sqlalchemy import func
from app.schemas.time_event import ClockedInEmployee

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/export-now")
async def export_now(
    export_date: Optional[date] = Query(None),
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """
    Trigger immediate export (admin)
    Exports specified date or yesterday if not specified
    """
    location = db.query(Location).filter(Location.id == device.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    if not export_date:
        import pytz
        from datetime import timedelta
        tz = pytz.timezone(location.timezone)
        export_date = (datetime.now(tz) - timedelta(days=1)).date()
    
    success = export_service.export_and_send(db, device.location_id, export_date)
    
    if success:
        return {
            "status": "ok",
            "message": f"Export sent for {export_date}",
            "date": export_date.isoformat()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed"
        )


@router.get("/stats")
async def get_stats(
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics (admin)"""
    # Total employees
    total_employees = db.query(Employee).filter(
        Employee.location_id == device.location_id,
        Employee.is_active == True
    ).count()
    
    # Currently clocked in
    employees = db.query(Employee).filter(
        Employee.location_id == device.location_id,
        Employee.is_active == True
    ).all()
    
    clocked_in_count = 0
    for employee in employees:
        state, _ = clock_logic_service.get_employee_state(
            db,
            employee.employee_id,
            str(employee.location_id)
        )
        if state == "CLOCKED_IN":
            clocked_in_count += 1
    
    # Today's events
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_events = db.query(TimeEvent).filter(
        TimeEvent.location_id == device.location_id,
        TimeEvent.event_time >= today_start
    ).count()
    
    return {
        "total_employees": total_employees,
        "clocked_in_count": clocked_in_count,
        "clocked_out_count": total_employees - clocked_in_count,
        "today_events": today_events
    }


@router.get("/clocked-in", response_model=List[ClockedInEmployee])
async def get_clocked_in(
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Get list of currently clocked in employees (admin)"""
    # Reuse the logic from time_events endpoint
    employees = db.query(Employee).filter(
        Employee.location_id == device.location_id,
        Employee.is_active == True
    ).all()
    
    clocked_in = []
    for emp in employees:
        state, last_event = clock_logic_service.get_employee_state(
            db,
            emp.employee_id,
            str(emp.location_id)
        )
        
        if state == "CLOCKED_IN" and last_event:
            device_info = db.query(Device).filter(Device.id == last_event.device_id).first()
            clocked_in.append(ClockedInEmployee(
                employee_id=emp.employee_id,
                name=emp.name,
                clock_in_time=last_event.event_time,
                device_id=last_event.device_id,
                device_name=device_info.name if device_info else None
            ))
    
    return clocked_in

