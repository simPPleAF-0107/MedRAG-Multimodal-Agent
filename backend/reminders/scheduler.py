import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

class ReminderScheduler:
    """
    Proactive background system designed to convert MedRAG from reactive into proactive.
    Sends push notifications/emails to patients to ensure treatment compliance.
    """
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}

    def start(self):
        """Starts the background scheduler loop."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("MedRAG Proactive Reminder Scheduler Started.")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("MedRAG Scheduler Stopped.")

    async def _send_notification(self, patient_id: str, message: str):
        """
        Mock function to push a notification or SMS to the patient.
        In production, this hooks into Firebase Cloud Messaging (FCM) or Twilio.
        """
        logger.info(f"==> [PROACTIVE PUSH NOTIFICATION] Patient {patient_id}: {message}")

    def schedule_daily_checkin(self, patient_id: str, diagnosis: str, activity_plan: str):
        """
        Schedules a daily follow-up to ask about their symptoms and remind them of the plan.
        """
        job_id = f"daily_checkin_{patient_id}"
        
        # Using interval seconds for prototype evaluation
        # Production: trigger="cron", hour=9
        message = f"MedRAG Follow-up: How are your symptoms regarding your {diagnosis} today? Keep up the plan: {activity_plan[:50]}..."
        
        self.scheduler.add_job(
            self._send_notification,
            'interval',
            seconds=60, # Fires every minute for immediate demo visibility
            args=[patient_id, message],
            id=job_id,
            replace_existing=True
        )
        self.jobs[patient_id] = job_id
        logger.info(f"Scheduled Daily Check-in for Patient {patient_id}")

reminder_scheduler = ReminderScheduler()
