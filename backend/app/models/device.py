from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String, unique=True, nullable=False)  # Hardware identifier
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    api_key = Column(String, nullable=False)  # Bcrypt hashed
    name = Column(String, nullable=True)  # Optional device name
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    location = relationship("Location", back_populates="devices")
    time_events = relationship("TimeEvent", back_populates="device")

