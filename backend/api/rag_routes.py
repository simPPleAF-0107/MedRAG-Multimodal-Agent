from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.database.db import get_db
from backend.core.pipeline import core_pipeline
from backend.rag.image.image_processor import image_processor
from backend.api.deps import get_current_doctor
from backend.database.models import User

router = APIRouter(
    prefix="/rag",
    tags=["rag"]
)

@router.post("/generate-report")
async def generate_report(
    query: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_doctor)
):
    """
    Generate a diagnosis report given a medical text query and optional image.
    This routes straight to the MedRAG core pipeline.
    """
    try:
        pil_image = None
        if image:
            # Quick check if it's an image
            if not image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="File must be an image.")
                
            contents = await image.read()
            pil_image = image_processor.load_image_from_bytes(contents)

        # Execute Modal RAG Pipeline
        result = await core_pipeline.run_multimodal_rag_pipeline(
            text_query=query,
            image=pil_image
        )

        return {"status": "success", "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any
from backend.utils.pdf_generator import generate_clinical_pdf
from datetime import datetime

class PipelineResult(BaseModel):
    result: Dict[str, Any]

@router.post("/export-pdf")
async def export_pdf(payload: PipelineResult, current_user: User = Depends(get_current_doctor)):
    """
    Export a previously generated Core Pipeline JSON result into a printable Clinical PDF.
    """
    try:
        pdf_path = f"medrag_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        generate_clinical_pdf(payload.result, pdf_path)
        return FileResponse(
            path=pdf_path, 
            filename="MedRAG_Clinical_Report.pdf", 
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
