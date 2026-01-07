from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import numpy as np
from pydantic import BaseModel
from app.database import get_db
from app.models.employee import Employee
from app.security import get_current_device
from app.services.face_service import face_service

router = APIRouter(prefix="/api/employees", tags=["embeddings"])


class EmbeddingStore(BaseModel):
    employee_id: str
    embedding: List[float]  # 512-dim embedding


class EmbeddingResponse(BaseModel):
    employee_id: str
    name: str
    embedding: List[float]


@router.post("/{employee_id}/embedding", status_code=status.HTTP_201_CREATED)
async def store_embedding(
    employee_id: UUID,
    embedding_data: EmbeddingStore,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """
    Store face embedding for an employee (admin)
    Expects 512-dim float array
    """
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.location_id == device.location_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    if employee.employee_id != embedding_data.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID mismatch"
        )
    
    # Convert list to numpy array
    embedding_array = np.array(embedding_data.embedding, dtype=np.float32)
    
    if embedding_array.shape != (512,):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Embedding must be 512 dimensions"
        )
    
    face_service.store_embedding(
        db,
        employee.employee_id,
        str(employee.location_id),
        embedding_array
    )
    
    return {"status": "ok", "message": "Embedding stored"}


@router.get("/embeddings", response_model=List[EmbeddingResponse])
async def get_embeddings(
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """
    Get all embeddings for device location (for sync)
    Returns decrypted embeddings for offline matching
    """
    embeddings_data = face_service.get_embeddings_for_sync(db, device.location_id)
    
    return [
        EmbeddingResponse(
            employee_id=e["employee_id"],
            name=e["name"],
            embedding=e["embedding"]
        )
        for e in embeddings_data
    ]


@router.delete("/{employee_id}/embedding", status_code=status.HTTP_204_NO_CONTENT)
async def delete_embedding(
    employee_id: UUID,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Delete face embedding for an employee (admin)"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.location_id == device.location_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    face_service.delete_embedding(
        db,
        employee.employee_id,
        str(employee.location_id)
    )
    
    return None

