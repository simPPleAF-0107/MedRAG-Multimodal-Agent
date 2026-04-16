from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List

from backend.database.db import get_db
from backend.database import crud, schemas
from backend.api.deps import get_current_doctor, get_current_active_user
from backend.database.models import User, Patient, Report

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

@router.get("/list/all")
async def list_all_patients(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    List all patients with dashboard summary fields.
    Doctors see their assigned patients; admins/patients see all.
    """
    if current_user.role == 'doctor':
        stmt = select(Patient).where(Patient.doctor_id == current_user.id)
    else:
        stmt = select(Patient)
    
    result = await db.execute(stmt)
    patients = result.scalars().all()
    
    patient_list = []
    for p in patients:
        # Count reports for confidence
        report_stmt = select(func.avg(Report.confidence_score)).where(Report.patient_id == p.id)
        conf_result = await db.execute(report_stmt)
        avg_conf = conf_result.scalar() or 0.0
        
        patient_list.append({
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "age": p.age,
            "sex": p.sex,
            "risk": p.risk or 0,
            "status": p.status or "Stable",
            "lastVisit": p.last_visit.strftime("%Y-%m-%d") if p.last_visit else "N/A",
            "confidence": round(avg_conf * 100) if avg_conf else 0,
            "blood_type": p.blood_type,
            "conditions": p.conditions,
        })
    
    return {"status": "success", "patients": patient_list, "total": len(patient_list)}

@router.get("/stats/summary")
async def patient_stats_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Aggregate patient stats for the dashboard: total, critical, avg risk, avg confidence.
    """
    if current_user.role == 'doctor':
        base_filter = Patient.doctor_id == current_user.id
    else:
        base_filter = True
    
    total = (await db.execute(select(func.count(Patient.id)).where(base_filter))).scalar() or 0
    critical = (await db.execute(select(func.count(Patient.id)).where(base_filter, Patient.status.in_(["Critical", "High Risk"])))).scalar() or 0
    avg_risk = (await db.execute(select(func.avg(Patient.risk)).where(base_filter))).scalar() or 0
    avg_conf = (await db.execute(select(func.avg(Report.confidence_score)))).scalar() or 0
    
    return {
        "status": "success",
        "total_patients": total,
        "critical_patients": critical,
        "avg_risk": round(avg_risk),
        "avg_confidence": round(avg_conf * 100) if avg_conf else 0,
    }

