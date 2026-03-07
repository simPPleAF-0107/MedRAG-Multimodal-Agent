from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.db import get_db

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/")
async def chat(
    message: str,
    patient_id: int = None,
    session_id: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Real-time interactive chat endpoint for doctors.
    Allows probing the MemoryAgent and RAG without creating full final reports.
    """
    # TODO: Connect Memory Agent and Retrieval for purely conversational queries
    
    return {
        "reply": f"Received: {message}. Conversational memory probing is pending explicit agent mapping."
    }
