from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.db import get_db
from backend.agents.router_agent import agentic_router
from backend.llm.openai_client import openai_client
from backend.core.agent_workflow import core_pipeline
from backend.database import crud

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

from backend.schemas.chat import ChatMessage

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
        if patient_id:
            from backend.services.patient_summarizer import summarize_patient_history
            reply = await summarize_patient_history(db, patient_id)
            if reply:
                return {"reply": reply, "route": category}
        
        return {
            "reply": "Please specify a valid patient ID to summarize their history, or ask a medical question.",
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

from fastapi.responses import StreamingResponse
import asyncio
import json as std_json

@router.post("/stream")
async def chat_stream(
    payload: ChatMessage,
    db: AsyncSession = Depends(get_db)
):
    """
    SSE Streaming endpoint for real-time typing effect on the UI.
    Yields Server-Sent Events (SSE).
    """
    async def event_generator():
        message = payload.message
        category = await agentic_router.route_query(message)
        
        # 1. Send Route metadata first
        yield f"data: {std_json.dumps({'type': 'meta', 'route': category})}\n\n"
        
        if category == "small_talk":
            # Simulate streaming words since openai_client doesn't expose async streaming in prototype
            reply = await openai_client.generate_completion(
                prompt=message,
                system_prompt="You are a helpful, friendly AI medical assistant.",
                use_cache=True
            )
            for chunk in reply.split():
                yield f"data: {std_json.dumps({'type': 'chunk', 'content': chunk + ' '})}\n\n"
                await asyncio.sleep(0.05)
                
        else:
            # Send status updates as pipeline runs
            yield f"data: {std_json.dumps({'type': 'status', 'content': 'Analyzing query...'})}\n\n"
            await asyncio.sleep(0.5)
            yield f"data: {std_json.dumps({'type': 'status', 'content': 'Extracting Knowledge Graph context...'})}\n\n"
            
            try:
                result = await core_pipeline.run_multimodal_rag_pipeline(text_query=message)
                
                reply = result.get("diagnosis", result.get("final_report", "Analysis Complete."))
                
                # Stream the final diagnosis words for the typing effect
                for chunk in reply.split():
                    yield f"data: {std_json.dumps({'type': 'chunk', 'content': chunk + ' '})}\n\n"
                    await asyncio.sleep(0.02)
                
                # Send the final pipeline data package
                pipeline_data = {
                    "confidence_score": result.get("confidence_score", 0),
                    "risk_score": result.get("risk_score", 0),
                    "emergency_flag": result.get("emergency_flag", False),
                    "recommended_specialty": result.get("recommended_specialty", "General")
                }
                yield f"data: {std_json.dumps({'type': 'done', 'pipeline_data': pipeline_data})}\n\n"
                
            except Exception as e:
                yield f"data: {std_json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
