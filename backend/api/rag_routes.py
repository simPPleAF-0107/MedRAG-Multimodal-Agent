from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.database.db import get_db
from backend.core.pipeline import core_pipeline
from backend.rag.image.image_processor import image_processor

router = APIRouter(
    prefix="/rag",
    tags=["rag"]
)

@router.post("/generate-report")
async def generate_report(
    query: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
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
