from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    employee_id = Column(String, nullable=False)  # Unique per location
    name = Column(String, nullable=False)
    pin_hash = Column(String, nullable=False)  # Bcrypt hash
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    location = relationship("Location", back_populates="employees")
    face_embeddings = relationship("FaceEmbedding", back_populates="employee", cascade="all, delete-orphan")
    time_events = relationship("TimeEvent", back_populates="employee")

    # Constraints
    __table_args__ = (
        UniqueConstraint("location_id", "employee_id", name="uq_location_employee_id"),
    )

