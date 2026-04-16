from backend.database import crud
from backend.llm.openai_client import openai_client

async def summarize_patient_history(db, patient_id: int) -> str:
    patient = await crud.get_patient_history(db, patient_id=patient_id)
    if not patient:
        return None
        
    history_text = f"Patient: {patient.first_name} {patient.last_name}\n"
    for r in patient.reports:
        history_text += f"- Report: {r.chief_complaint} \u2192 {r.final_report[:200]}\n"
    
    reply = await openai_client.generate_completion(
        prompt=f"Summarize this patient's medical history concisely:\n{history_text}",
        system_prompt="You are a medical summarization assistant. Provide concise, structured summaries.",
        use_cache=True
    )
    return reply
