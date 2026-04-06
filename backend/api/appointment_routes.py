from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Any

from backend.database.db import get_db
from backend.database.models import User, Appointment, Notification, Patient
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
        status="pending"
    )
    db.add(new_app)
    await db.flush()
    
    # Notify the doctor
    notification = Notification(
        user_id=new_app.doctor_id,
        message=f"New appointment request for {new_app.appointment_date.strftime('%Y-%m-%d %H:%M')}. Reason: {new_app.reason or 'Not provided'}",
        appointment_id=new_app.id
    )
    db.add(notification)
    
    await db.commit()
    await db.refresh(new_app)
    return new_app

@router.patch("/appointments/{appointment_id}/status", response_model=schemas.AppointmentResponse)
async def update_appointment_status(
    appointment_id: int,
    payload: schemas.AppointmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    # Fetch appointment
    query = select(Appointment).where(Appointment.id == appointment_id)
    result = await db.execute(query)
    appointment = result.scalars().first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    # Verify doctor owns this appointment
    if current_user.role == "doctor" and appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this appointment")
        
    appointment.status = payload.status
    
    # Fetch patient to notify
    patient_query = select(Patient).where(Patient.id == appointment.patient_id)
    p_result = await db.execute(patient_query)
    patient = p_result.scalars().first()
    
    if patient and patient.user_account_id:
        # Notify the patient
        notif = Notification(
            user_id=patient.user_account_id,
            message=f"Your appointment on {appointment.appointment_date.strftime('%Y-%m-%d %H:%M')} has been {payload.status}.",
            appointment_id=appointment.id
        )
        db.add(notif)
        
    # Mark related unread notifications for this doctor as read
    notif_query = select(Notification).where(
        Notification.appointment_id == appointment.id,
        Notification.user_id == appointment.doctor_id,
        Notification.is_read == False
    )
    n_result = await db.execute(notif_query)
    for n in n_result.scalars().all():
        n.is_read = True
        
    await db.commit()
    await db.refresh(appointment)
    return appointment

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
