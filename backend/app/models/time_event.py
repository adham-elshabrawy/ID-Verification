from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class TimeEvent(Base):
    __tablename__ = "time_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    event_type = Column(String, nullable=False)  # 'IN' or 'OUT'
    event_time = Column(TIMESTAMP(timezone=True), nullable=False)
    method = Column(String, nullable=False)  # 'FACE' or 'PIN'
    is_valid = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="time_events")
    device = relationship("Device", back_populates="time_events")
    location = relationship("Location", back_populates="time_events")

