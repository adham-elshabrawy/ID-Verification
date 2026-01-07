from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, Tuple
from app.models.employee import Employee
from app.models.time_event import TimeEvent


class ClockState:
    CLOCKED_IN = "CLOCKED_IN"
    CLOCKED_OUT = "CLOCKED_OUT"


class ClockLogicService:
    """Service for calculating clock state and validating transitions"""

    @staticmethod
    def get_employee_state(db: Session, employee_id: str, location_id: str) -> Tuple[str, Optional[TimeEvent]]:
        """
        Get current clock state for an employee
        
        Returns:
            Tuple of (state, last_event)
        """
        employee = db.query(Employee).filter(
            Employee.employee_id == employee_id,
            Employee.location_id == location_id
        ).first()
        
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        # Get latest valid event
        last_event = db.query(TimeEvent).filter(
            TimeEvent.employee_id == employee.id,
            TimeEvent.is_valid == True
        ).order_by(desc(TimeEvent.event_time)).first()
        
        if not last_event or last_event.event_type == "OUT":
            return ClockState.CLOCKED_OUT, last_event
        
        return ClockState.CLOCKED_IN, last_event

    @staticmethod
    def can_clock_in(db: Session, employee_id: str, location_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if employee can clock in
        
        Returns:
            Tuple of (can_clock_in, error_message)
        """
        try:
            state, last_event = ClockLogicService.get_employee_state(db, employee_id, location_id)
            
            if state == ClockState.CLOCKED_IN:
                if last_event:
                    event_time_str = last_event.event_time.strftime("%H:%M")
                    return False, f"You are already clocked in since {event_time_str}"
                return False, "You are already clocked in"
            
            return True, None
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def can_clock_out(db: Session, employee_id: str, location_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if employee can clock out
        
        Returns:
            Tuple of (can_clock_out, error_message)
        """
        try:
            state, last_event = ClockLogicService.get_employee_state(db, employee_id, location_id)
            
            if state == ClockState.CLOCKED_OUT:
                if last_event:
                    return False, "You must clock in before clocking out"
                return False, "You are not clocked in"
            
            return True, None
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def validate_event(
        db: Session,
        employee_id: str,
        location_id: str,
        event_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if an event can be created
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if event_type == "IN":
            return ClockLogicService.can_clock_in(db, employee_id, location_id)
        elif event_type == "OUT":
            return ClockLogicService.can_clock_out(db, employee_id, location_id)
        else:
            return False, f"Invalid event type: {event_type}"

    @staticmethod
    def recalculate_employee_state(db: Session, employee_id: str, location_id: str) -> str:
        """
        Recalculate and return employee state (useful after admin corrections)
        """
        state, _ = ClockLogicService.get_employee_state(db, employee_id, location_id)
        return state


clock_logic_service = ClockLogicService()

