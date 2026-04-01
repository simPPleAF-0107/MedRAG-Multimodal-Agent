from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.db import get_db
from backend.agents.router_agent import agentic_router
from backend.llm.openai_client import openai_client
from backend.core.pipeline import core_pipeline
from backend.database import crud

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

class ChatMessage(BaseModel):
    message: str
    patient_id: Optional[int] = None
    session_id: Optional[str] = None

@router.post("/")
async def chat(
    payload: ChatMessage,
    db: AsyncSession = Depends(get_db)
):
    """
    Real-time interactive chat endpoint for doctors.
    Routes queries dynamically based on Agentic classification to save costs.
    Also supports legacy query-param format for backwards compatibility.
    """
    message = payload.message
    patient_id = payload.patient_id
    
    category = await agentic_router.route_query(message)
    
    if category == "small_talk":
        reply = await openai_client.generate_completion(
            prompt=message,
            system_prompt="You are a helpful, friendly AI medical assistant. Answer pleasantly but concisely.",
            use_cache=True
        )
        return {"reply": reply, "route": category}
        
    elif category == "summarization":
        # Attempt to fetch patient history and summarize
        if patient_id:
            patient = await crud.get_patient_history(db, patient_id=patient_id)
            if patient:
                history_text = f"Patient: {patient.first_name} {patient.last_name}\n"
                for r in patient.reports:
                    history_text += f"- Report: {r.chief_complaint} → {r.final_report[:200]}\n"
                
                reply = await openai_client.generate_completion(
                    prompt=f"Summarize this patient's medical history concisely:\n{history_text}",
                    system_prompt="You are a medical summarization assistant. Provide concise, structured summaries.",
                    use_cache=True
                )
                return {"reply": reply, "route": category}
        
        return {
            "reply": "Please specify a patient ID to summarize their history, or ask a medical question.",
            "route": category
        }
        
    else:  # clinical_query — run the full RAG pipeline
        try:
            result = await core_pipeline.run_multimodal_rag_pipeline(
                text_query=message
            )
            return {
                "reply": result.get("diagnosis", result.get("final_report", "Pipeline completed but no diagnosis generated.")),
                "route": category,
                "pipeline_data": {
                    "confidence_score": result.get("confidence_score", 0),
                    "risk_score": result.get("risk_score", 0),
                    "emergency_flag": result.get("emergency_flag", False),
                    "differential_diagnosis": result.get("differential_diagnosis", []),
                    "recommendations": result.get("recommendations", {})
                }
            }
        except Exception as e:
            return {
                "reply": f"Clinical analysis encountered an error: {str(e)}. Please try again.",
                "route": category
            }
