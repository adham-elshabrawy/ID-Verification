from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import datetime, time
import pytz
from app.database import SessionLocal
from app.models.location import Location
from app.services.export_service import export_service


class SchedulerService:
    """Service for scheduling daily exports"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self._schedule_exports()
            self.scheduler.start()
            self.is_running = True

    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False

    def _schedule_exports(self):
        """Schedule daily exports for all locations"""
        # This should be called after app startup
        # For now, we'll schedule a job that runs daily and checks all locations
        # In production, you might want individual jobs per location
        
        async def daily_export_job():
            """Job that runs daily and exports yesterday's data for all locations"""
            db = SessionLocal()
            try:
                locations = db.query(Location).filter(Location.manager_email != "").all()
                for location in locations:
                    export_service.export_yesterday_for_location(db, location.id)
            finally:
                db.close()
        
        # Schedule to run daily at 1 AM UTC (adjust as needed)
        self.scheduler.add_job(
            daily_export_job,
            trigger=CronTrigger(hour=1, minute=0),
            id="daily_export",
            replace_existing=True
        )


scheduler_service = SchedulerService()

