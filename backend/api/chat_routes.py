from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.db import get_db
from backend.agents.router_agent import agentic_router
from backend.llm.openai_client import openai_client

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
    Routes queries dynamically based on Agentic classification to save costs.
    """
    category = await agentic_router.route_query(message)
    
    if category == "small_talk":
        reply = await openai_client.generate_completion(
            prompt=message,
            system_prompt="You are a helpful, friendly AI medical assistant. Answer pleasantly but concisely.",
            use_cache=True
        )
        return {"reply": reply, "route": category}
        
    elif category == "summarization":
        # Future-proofing for patient history extraction
        return {"reply": f"Routing to patient history summarization module... (Pending full database vectorization for patient ID {patient_id})", "route": category}
        
    else: # clinical_query
        return {
            "reply": f"Triggering deep MedRAG pipeline. Evaluating clinical context for: '{message}'", 
            "route": category
        }
