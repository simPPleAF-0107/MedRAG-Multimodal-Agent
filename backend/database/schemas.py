from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Extended Health Log Schemas ---

class MoodLogBase(BaseModel):
    mood_score: int
    notes: Optional[str] = None

class MoodLogCreate(MoodLogBase):
    patient_id: int

class MoodLogResponse(MoodLogBase):
    id: int
    patient_id: int
    recorded_at: datetime
    class Config:
        from_attributes = True

class ActivityLogBase(BaseModel):
    activity_type: str
    duration_minutes: int
    intensity: Optional[str] = None

class ActivityLogCreate(ActivityLogBase):
    patient_id: int

class ActivityLogResponse(ActivityLogBase):
    id: int
    patient_id: int
    recorded_at: datetime
    class Config:
        from_attributes = True

class CycleLogBase(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None
    symptoms: Optional[str] = None

class CycleLogCreate(CycleLogBase):
    patient_id: int

class CycleLogResponse(CycleLogBase):
    id: int
    patient_id: int
    recorded_at: datetime
    class Config:
        from_attributes = True

# --- Report Schemas ---

class ReportBase(BaseModel):
    chief_complaint: str
    diagnosis_reasoning: str
    final_report: str
    retrieved_evidence: Optional[str] = None
    confidence_score: Optional[float] = None
    risk_score: Optional[float] = None
    hallucination_score: Optional[float] = None
    emergency_flag: Optional[bool] = None
    recommended_specialty: Optional[str] = None

class ReportCreate(ReportBase):
    patient_id: int

class ReportResponse(ReportBase):
    id: int
    patient_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Patient Schemas ---

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    sex: Optional[str] = None
    medical_history_summary: Optional[str] = None
    user_account_id: Optional[int] = None

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    doctor_id: int
    created_at: datetime
    reports: List[ReportResponse] = []
    mood_logs: List[MoodLogResponse] = []
    activity_logs: List[ActivityLogResponse] = []
    cycle_logs: List[CycleLogResponse] = []

    class Config:
        from_attributes = True

# --- User Schemas ---

class UserBase(BaseModel):
    username: str
    email: str
    role: str = "doctor"
    specialty: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "doctor"

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- AI Feedback Schemas ---

class AIFeedbackBase(BaseModel):
    report_id: int
    is_approved: bool
    correction_notes: Optional[str] = None

class AIFeedbackCreate(AIFeedbackBase):
    pass

class AIFeedbackResponse(AIFeedbackBase):
    id: int
    doctor_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Appointment Schemas ---

class AppointmentBase(BaseModel):
    appointment_date: datetime
    status: str = "scheduled"
    reason: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    patient_id: int
    doctor_id: int

class AppointmentResponse(AppointmentBase):
    id: int
    patient_id: int
    doctor_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
