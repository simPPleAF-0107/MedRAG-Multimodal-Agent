from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Any

from backend.database.db import get_db
from backend.database.models import User, Appointment
from backend.database import schemas
from backend.api.deps import get_current_active_user

router = APIRouter(tags=["Appointments"])

@router.post("/appointments/book", response_model=schemas.AppointmentResponse)
async def book_appointment(
    payload: schemas.AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    new_app = Appointment(
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        appointment_date=payload.appointment_date,
        reason=payload.reason,
        status=payload.status or "scheduled"
    )
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)
    return new_app

@router.get("/appointments/patient/{patient_id}", response_model=List[schemas.AppointmentResponse])
async def get_patient_appointments(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    query = select(Appointment).where(Appointment.patient_id == patient_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/doctors/specialty/{specialty}", response_model=List[schemas.UserResponse])
async def get_doctors_by_specialty(
    specialty: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    query = select(User).where(User.role == "doctor", User.specialty == specialty)
    result = await db.execute(query)
    return result.scalars().all()
