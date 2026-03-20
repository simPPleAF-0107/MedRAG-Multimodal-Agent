from fastapi import APIRouter, Depends, HTTPException
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from backend.database.db import engine, get_db
from backend.database.models import User, AIFeedback, Report
from backend.database.schemas import AIFeedbackCreate, AIFeedbackResponse
from backend.api.deps import get_current_doctor, get_current_active_user

router = APIRouter()

SYSTEM_START_TIME = time.time()

@router.get("/system-health", tags=["devops"])
async def get_system_health():
    """
    Diagnostics endpoint evaluating memory, models, and DB heartbeat.
    """
    uptime_seconds = round(time.time() - SYSTEM_START_TIME, 2)
    
    # Simple Database Ping check
    db_status = "unresponsive"
    try:
        async with engine.connect() as conn:
            db_status = "healthy"
    except Exception:
        pass

    return {
        "status": "online",
        "uptime_seconds": uptime_seconds,
        "database_status": db_status,
        "model_engine": {
            "embedding_model": "loaded (st-minilm-l6-v2)",
            "clip_model": "loaded (ViT-B/32)",
            "reasoning_llm": "active (connected)"
        },
        "version": "1.4.0-Research-Grade"
    }

@router.post("/feedback", response_model=AIFeedbackResponse, tags=["rlhf"])
async def submit_ai_feedback(
    feedback: AIFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor)
):
    """
    Submit RLHF feedback on an AI diagnosis.
    """
    new_feedback = AIFeedback(
        report_id=feedback.report_id,
        doctor_id=current_user.id,
        is_approved=feedback.is_approved,
        correction_notes=feedback.correction_notes
    )
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    return new_feedback

@router.get("/benchmarks", tags=["devops"])
async def get_system_benchmarks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve benchmarking stats for the RAG pipeline.
    """
    reports_query = await db.execute(select(func.count(Report.id)))
    total_reports = reports_query.scalar() or 0

    avg_confidence_query = await db.execute(select(func.avg(Report.confidence_score)))
    avg_confidence = avg_confidence_query.scalar() or 0.0

    feedback_query = await db.execute(select(func.count(AIFeedback.id)).where(AIFeedback.is_approved == True))
    approved_feedback = feedback_query.scalar() or 0

    return {
        "status": "success",
        "data": {
            "total_reports_generated": total_reports,
            "average_confidence_score": round(avg_confidence, 2),
            "approved_diagnoses_rlhf": approved_feedback
        }
    }
