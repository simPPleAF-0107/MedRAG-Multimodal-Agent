from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.database.db import get_db
from backend.core.pipeline import core_pipeline
from backend.rag.image.image_processor import image_processor
from backend.api.deps import get_current_doctor, get_current_active_user
from backend.database.models import User

router = APIRouter(
    prefix="/rag",
    tags=["rag"]
)

from typing import Optional, List

@router.post("/generate-report")
async def generate_report(
    query: str = Form(...),
    files: List[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a diagnosis report given a medical text query and multiple optional images/texts.
    Concatenates text documents to the query and passes images individually to the RAG pipeline.
    """
    try:
        texts = []
        images = []
        for file in files:
            # Check content type and extension
            if file.content_type.startswith("text/") or file.filename.endswith((".txt", ".md", ".csv")):
                content = await file.read()
                texts.append(content.decode("utf-8", errors="ignore"))
            elif file.content_type.startswith("image/"):
                contents = await file.read()
                images.append(image_processor.load_image_from_bytes(contents))

        # Concatenate text to query
        combined_query = query
        if texts:
            combined_query += "\n\n[Provided Clinical Documents]:\n" + "\n---\n".join(texts)

        # Run pipeline
        results = []
        if not images:
            results.append(await core_pipeline.run_multimodal_rag_pipeline(text_query=combined_query, image=None))
        else:
            for img in images:
                res = await core_pipeline.run_multimodal_rag_pipeline(text_query=combined_query, image=img)
                results.append(res)

        # Merge results for frontend payload
        final_result = results[0].copy()
        if len(results) > 1:
            for i, res in enumerate(results[1:], start=2):
                final_result["diagnosis"] += f"\n\n--- Image {i} Analysis ---\n{res['diagnosis']}"
                if res.get("evidence"):
                    final_result["evidence"] += f"\n\n--- Image {i} Evidence ---\n{res['evidence']}"
                
                # Combine alias representations as well so UI renders it!
                if "final_report" in final_result:
                     final_result["final_report"] += f"\n\n--- Image {i} Analysis ---\n{res['diagnosis']}"
        final_result["status"] = "success"
        final_result["query"] = query  # Include original query for frontend display
        return final_result
        
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
