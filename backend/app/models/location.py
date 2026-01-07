from sqlalchemy import Column, String, Time, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    manager_email = Column(String, nullable=False)
    export_time = Column(Time, nullable=False)  # Daily export time
    timezone = Column(String, nullable=False, default="America/Toronto")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    devices = relationship("Device", back_populates="location", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="location", cascade="all, delete-orphan")
    time_events = relationship("TimeEvent", back_populates="location")
    settings = relationship("Settings", back_populates="location", cascade="all, delete-orphan")

