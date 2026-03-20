from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.database.db import get_db
from backend.database import crud, schemas
from backend.api.deps import get_current_doctor, get_current_active_user
from backend.database.models import User

router = APIRouter(
    prefix="/patient",
    tags=["patient"]
)

@router.get("/{patient_id}/history", response_model=schemas.PatientResponse)
async def get_history(patient_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Retrieve full longitudinal history of a patient.
    Includes reports, mood logs, activity logs, and cycle logs.
    """
    patient = await crud.get_patient_history(db, patient_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.post("/", response_model=schemas.PatientResponse)
async def create_new_patient(patient: schemas.PatientCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_doctor)):
    # Automatically assign the patient to the logged-in doctor
    doctor_id = current_user.id 
    return await crud.create_patient(db, patient=patient, doctor_id=doctor_id)
