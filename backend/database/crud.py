from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.database import models, schemas
import hashlib

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_patient(db: AsyncSession, patient: schemas.PatientCreate, doctor_id: int):
    db_patient = models.Patient(
        **patient.model_dump(),
        doctor_id=doctor_id
    )
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    return db_patient

async def get_patient_history(db: AsyncSession, patient_id: int):
    """
    Returns full longitudinal history of a patient, including
    reports, mood logs, activity logs, and cycle logs.
    Utilizes selectinload to eagerly fetch relationships optimally.
    """
    stmt = (
        select(models.Patient)
        .options(
            selectinload(models.Patient.reports),
            selectinload(models.Patient.mood_logs),
            selectinload(models.Patient.activity_logs),
            selectinload(models.Patient.cycle_logs)
        )
        .filter(models.Patient.id == patient_id)
    )
    result = await db.execute(stmt)
    patient = result.scalars().first()
    return patient

# --- Record Creation Extensibility ---

async def store_report(db: AsyncSession, report: schemas.ReportCreate):
    db_report = models.Report(**report.model_dump())
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report

async def store_mood_log(db: AsyncSession, log: schemas.MoodLogCreate):
    db_log = models.MoodLog(**log.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def store_activity_log(db: AsyncSession, log: schemas.ActivityLogCreate):
    db_log = models.ActivityLog(**log.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def store_cycle_log(db: AsyncSession, log: schemas.CycleLogCreate):
    db_log = models.CycleLog(**log.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log
