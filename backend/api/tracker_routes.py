from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.db import get_db
from backend.database.models import User
from backend.api.deps import get_optional_user
from backend.llm.openai_client import openai_client
from backend.utils.logger import logger

router = APIRouter(prefix="/tracker", tags=["tracker"])


class TrackerSuggestRequest(BaseModel):
    type: str  # "meal" | "activity" | "mood" | "cycle"
    logs: List[Dict[str, Any]] = []
    patient_context: Optional[Dict[str, Any]] = None


# Domain-specific system prompts for each tracker type
TRACKER_PROMPTS = {
    "meal": (
        "You are a clinical nutrition AI assistant. Based on the patient's recent meal logs "
        "and medical conditions, generate a personalized 7-day meal plan. Focus on:\n"
        "- Anti-inflammatory foods if inflammatory conditions are present\n"
        "- Macro balance (protein, carbs, fats) tailored to their health goals\n"
        "- Foods to avoid based on their conditions and medications\n"
        "- Specific meal suggestions for breakfast, lunch, dinner, and snacks\n"
        "Format the response in clear markdown with days as headers."
    ),
    "activity": (
        "You are a clinical exercise physiology AI. Based on the patient's recent activity logs "
        "and medical conditions, generate a personalized weekly activity plan. Include:\n"
        "- Safe exercise types considering their conditions\n"
        "- Duration and intensity targets with heart rate zones\n"
        "- Recovery and rest day recommendations\n"
        "- Progression suggestions for the coming weeks\n"
        "Format the response in clear markdown with days as headers."
    ),
    "mood": (
        "You are a psychiatric wellness AI assistant. Analyze the patient's recent mood and "
        "stress logs to provide clinical insights. Include:\n"
        "- Mood trend analysis (improving, declining, stable)\n"
        "- Potential trigger identification based on patterns\n"
        "- Evidence-based coping strategies\n"
        "- Sleep hygiene recommendations if sleep quality is poor\n"
        "- When to seek professional help flags\n"
        "Format the response in clear markdown with section headers."
    ),
    "cycle": (
        "You are a reproductive health AI assistant. Analyze the patient's cycle tracking data "
        "to provide clinical insights. Include:\n"
        "- Cycle regularity assessment\n"
        "- Predicted next cycle start date (based on average cycle length)\n"
        "- Symptom management recommendations for reported symptoms\n"
        "- When patterns may warrant clinical attention\n"
        "- Lifestyle adjustments for different cycle phases\n"
        "Format the response in clear markdown with section headers."
    ),
}


@router.post("/suggest")
async def get_tracker_suggestion(
    payload: TrackerSuggestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Generate AI-powered suggestions for any tracker type (meal, activity, mood, cycle).
    Sends recent logs + patient context to the LLM and returns a structured recommendation.
    """
    tracker_type = payload.type.lower()
    system_prompt = TRACKER_PROMPTS.get(tracker_type)

    if not system_prompt:
        return {
            "status": "error",
            "suggestion": f"Unknown tracker type: '{tracker_type}'. Supported: meal, activity, mood, cycle."
        }

    # Build the user-facing prompt from logs
    log_summary = "No recent logs provided."
    if payload.logs:
        log_lines = []
        for i, log in enumerate(payload.logs[:15], 1):  # cap at 15 most recent
            log_lines.append(f"  {i}. {log}")
        log_summary = "\n".join(log_lines)

    context_text = ""
    if payload.patient_context:
        conditions = payload.patient_context.get("conditions", [])
        medications = payload.patient_context.get("medications", [])
        if conditions:
            context_text += f"\nMedical Conditions: {', '.join(conditions)}"
        if medications:
            context_text += f"\nCurrent Medications: {', '.join(medications)}"

    user_prompt = (
        f"Patient's recent {tracker_type} logs:\n{log_summary}\n"
        f"{context_text}\n\n"
        f"Based on this data, provide your personalized {tracker_type} recommendations."
    )

    try:
        logger.info(f"[Tracker AI] Generating {tracker_type} suggestion for user {current_user.id if current_user else 'demo'}")
        suggestion = await openai_client.generate_completion(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.4,
            max_tokens=1500,
            use_cache=False,
        )
        return {"status": "success", "type": tracker_type, "suggestion": suggestion}

    except Exception as e:
        logger.error(f"[Tracker AI] Failed to generate suggestion: {e}")
        return {
            "status": "error",
            "type": tracker_type,
            "suggestion": f"Failed to generate AI suggestion: {str(e)}. Please try again.",
        }
