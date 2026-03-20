from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default="doctor", nullable=False) # Roles: doctor, patient, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    patients = relationship("Patient", back_populates="doctor")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_account_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True) # Link to patient's auth account
    doctor_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(DateTime)
    medical_history_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user_account = relationship("User", foreign_keys=[user_account_id])
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="patients")
    reports = relationship("Report", back_populates="patient")
    mood_logs = relationship("MoodLog", back_populates="patient")
    activity_logs = relationship("ActivityLog", back_populates="patient")
    cycle_logs = relationship("CycleLog", back_populates="patient")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    chief_complaint = Column(Text, nullable=False)
    diagnosis_reasoning = Column(Text, nullable=False)
    final_report = Column(Text, nullable=False)
    retrieved_evidence = Column(Text, nullable=True) # Explicitly store evidence
    confidence_score = Column(Float, nullable=True) # Calibrated score
    risk_score = Column(Float, nullable=True)
    hallucination_score = Column(Float, nullable=True)
    emergency_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    patient = relationship("Patient", back_populates="reports")

# --- Extended Health Logs ---

class MoodLog(Base):
    __tablename__ = "mood_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    mood_score = Column(Integer, nullable=False) # e.g. 1-10
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="mood_logs")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    activity_type = Column(String(50), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    intensity = Column(String(20)) # Low, Medium, High
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="activity_logs")

class CycleLog(Base):
    __tablename__ = "cycle_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    symptoms = Column(Text, nullable=True) # Comma separated or JSON string
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="cycle_logs")

class AIFeedback(Base):
    """
    Stores Human-in-the-Loop feedback from doctors to fine-tune the RAG model.
    """
    __tablename__ = "ai_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_approved = Column(Boolean, nullable=False)
    correction_notes = Column(Text, nullable=True) # If rejected, what was wrong?
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    report = relationship("Report")
    doctor = relationship("User")
