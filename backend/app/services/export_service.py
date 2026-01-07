from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date, time, timedelta
from typing import List, Optional
import csv
import io
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment
from app.models.location import Location
from app.models.time_event import TimeEvent
from app.models.employee import Employee
from app.models.device import Device
from app.config import settings
import pytz
from uuid import UUID


class ExportService:
    """Service for generating and emailing CSV exports"""

    def __init__(self):
        self.sendgrid_client = None
        if settings.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(settings.sendgrid_api_key)

    def generate_csv(
        self,
        db: Session,
        location_id: UUID,
        export_date: date
    ) -> str:
        """
        Generate CSV content for a specific date
        
        Returns CSV string
        """
        # Get location with timezone
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise ValueError(f"Location {location_id} not found")
        
        tz = pytz.timezone(location.timezone)
        
        # Get start and end of day in location timezone
        start_dt = tz.localize(datetime.combine(export_date, time.min))
        end_dt = tz.localize(datetime.combine(export_date, time.max))
        
        # Convert to UTC for database query
        start_utc = start_dt.astimezone(pytz.UTC).replace(tzinfo=None)
        end_utc = end_dt.astimezone(pytz.UTC).replace(tzinfo=None)
        
        # Query events
        events = db.query(TimeEvent).join(Employee).join(Device).filter(
            and_(
                TimeEvent.location_id == location_id,
                TimeEvent.event_time >= start_utc,
                TimeEvent.event_time <= end_utc
            )
        ).order_by(TimeEvent.event_time).all()
        
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Date",
            "Time",
            "Employee ID",
            "Employee Name",
            "Event Type",
            "Location Name",
            "Device ID",
            "Method",
            "Valid"
        ])
        
        # Rows
        for event in events:
            # Convert to location timezone
            event_time_local = event.event_time.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            writer.writerow([
                event_time_local.strftime("%Y-%m-%d"),
                event_time_local.strftime("%H:%M:%S"),
                event.employee.employee_id,
                event.employee.name,
                event.event_type,
                location.name,
                event.device.device_id,
                event.method,
                str(event.is_valid).lower()
            ])
        
        return output.getvalue()

    def send_csv_email(
        self,
        csv_content: str,
        recipient_email: str,
        export_date: date
    ) -> bool:
        """
        Send CSV as email attachment via SendGrid
        
        Returns True if successful
        """
        if not self.sendgrid_client:
            raise ValueError("SendGrid API key not configured")
        
        # Create email
        message = Mail(
            from_email="noreply@kioskapp.com",  # Configure in settings
            to_emails=recipient_email,
            subject=f"Daily Time Event Export - {export_date.strftime('%Y-%m-%d')}",
            html_content=f"<p>Please find attached the daily time event export for {export_date.strftime('%Y-%m-%d')}.</p>"
        )
        
        # Create attachment
        encoded_csv = csv_content.encode('utf-8')
        attachment = Attachment()
        attachment.file_content = encoded_csv
        attachment.file_type = "text/csv"
        attachment.file_name = f"time_events_{export_date.strftime('%Y%m%d')}.csv"
        attachment.disposition = "attachment"
        
        message.add_attachment(attachment)
        
        try:
            response = self.sendgrid_client.send(message)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def export_and_send(
        self,
        db: Session,
        location_id: UUID,
        export_date: date
    ) -> bool:
        """
        Generate CSV and send via email for a location/date
        
        Returns True if successful
        """
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location or not location.manager_email:
            return False
        
        try:
            csv_content = self.generate_csv(db, location_id, export_date)
            return self.send_csv_email(csv_content, location.manager_email, export_date)
        except Exception as e:
            print(f"Error in export_and_send: {e}")
            return False

    def export_yesterday_for_location(
        self,
        db: Session,
        location_id: UUID
    ) -> bool:
        """
        Export yesterday's data for a location
        """
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            return False
        
        tz = pytz.timezone(location.timezone)
        yesterday = (datetime.now(tz) - timedelta(days=1)).date()
        
        return self.export_and_send(db, location_id, yesterday)


export_service = ExportService()

