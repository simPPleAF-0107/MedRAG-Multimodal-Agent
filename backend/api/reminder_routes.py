from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.reminders.scheduler import reminder_scheduler
from backend.api.deps import get_current_active_user
from backend.database.models import User

router = APIRouter(prefix="/reminders", tags=["Proactive Reminders Engine"])

class ReminderSubscription(BaseModel):
    patient_id: str
    diagnosis: str
    activity_plan: str

@router.post("/subscribe")
async def subscribe_reminders(payload: ReminderSubscription, current_user: User = Depends(get_current_active_user)):
    """
    Subscribes the patient to daily push/SMS notifications regarding their AI diagnosis and treatment plan.
    """
    reminder_scheduler.schedule_daily_checkin(
        patient_id=payload.patient_id,
        diagnosis=payload.diagnosis,
        activity_plan=payload.activity_plan
    )
    return {"status": "success", "message": f"Patient {payload.patient_id} successfully subscribed to Daily Insight Reminders."}
