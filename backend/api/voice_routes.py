import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.llm.openai_client import openai_client
from backend.core.pipeline import core_pipeline

router = APIRouter(prefix="/voice", tags=["Voice Symptom Recognition"])

@router.post("/transcribe_and_run")
async def transcribe_and_run(audio: UploadFile = File(...)):
    """
    Accepts a voice note of a patient's symptoms, transcribes it via Whisper, 
    and then immediately pipes the transcript into the Multimodal pipeline.
    """
    # Accept mp3, wav, m4a etc.
    temp_path = f"temp_audio_{audio.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
        # 1. Transcribe Voice to Text
        transcript = await openai_client.generate_transcription(temp_path)
        
        # 2. Run Pipeline contextually
        result = await core_pipeline.run_multimodal_rag_pipeline(text_query=transcript)
        
        return {
            "transcript": transcript,
            "pipeline_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio transcription failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
