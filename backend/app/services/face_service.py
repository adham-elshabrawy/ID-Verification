from sqlalchemy.orm import Session
from typing import List, Optional
import numpy as np
from app.models.employee import Employee
from app.models.face_embedding import FaceEmbedding
from app.services.encryption import encryption_service
from datetime import datetime


class FaceService:
    """Service for managing face embeddings"""

    @staticmethod
    def store_embedding(
        db: Session,
        employee_id: str,
        location_id: str,
        embedding: np.ndarray
    ) -> FaceEmbedding:
        """
        Store an encrypted face embedding for an employee
        
        Args:
            db: Database session
            employee_id: Employee ID string
            location_id: Location UUID
            embedding: 512-dim numpy array (float32)
            
        Returns:
            FaceEmbedding model instance
        """
        # Get employee
        employee = db.query(Employee).filter(
            Employee.employee_id == employee_id,
            Employee.location_id == location_id
        ).first()
        
        if not employee:
            raise ValueError(f"Employee {employee_id} not found at location")
        
        # Encrypt embedding
        encrypted_data, key_id = encryption_service.encrypt_embedding(embedding)
        
        # Create or update embedding (one embedding per employee for MVP)
        existing = db.query(FaceEmbedding).filter(
            FaceEmbedding.employee_id == employee.id
        ).first()
        
        if existing:
            existing.embedding_encrypted = encrypted_data
            existing.encryption_key_id = key_id
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            face_embedding = FaceEmbedding(
                employee_id=employee.id,
                embedding_encrypted=encrypted_data,
                encryption_key_id=key_id
            )
            db.add(face_embedding)
            db.commit()
            db.refresh(face_embedding)
            return face_embedding

    @staticmethod
    def get_embeddings_for_sync(
        db: Session,
        location_id: str
    ) -> List[dict]:
        """
        Get all embeddings for a location (decrypted, for device sync)
        Returns list of dicts with employee_id, name, and embedding array
        """
        employees = db.query(Employee).filter(
            Employee.location_id == location_id,
            Employee.is_active == True
        ).all()
        
        result = []
        for employee in employees:
            embedding_record = db.query(FaceEmbedding).filter(
                FaceEmbedding.employee_id == employee.id
            ).first()
            
            if embedding_record:
                # Decrypt embedding
                embedding = encryption_service.decrypt_embedding(
                    embedding_record.embedding_encrypted,
                    embedding_record.encryption_key_id
                )
                
                result.append({
                    "employee_id": employee.employee_id,
                    "name": employee.name,
                    "embedding": embedding.tolist()  # Convert to list for JSON
                })
        
        return result

    @staticmethod
    def delete_embedding(
        db: Session,
        employee_id: str,
        location_id: str
    ) -> bool:
        """
        Delete face embedding for an employee
        """
        employee = db.query(Employee).filter(
            Employee.employee_id == employee_id,
            Employee.location_id == location_id
        ).first()
        
        if not employee:
            return False
        
        embedding = db.query(FaceEmbedding).filter(
            FaceEmbedding.employee_id == employee.id
        ).first()
        
        if embedding:
            db.delete(embedding)
            db.commit()
            return True
        
        return False


face_service = FaceService()

