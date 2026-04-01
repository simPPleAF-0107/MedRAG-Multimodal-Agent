from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from backend.utils.file_handler import file_handler

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

@router.post("/record")
async def upload_record(
    file: UploadFile = File(...),
    patient_id: Optional[int] = Form(None),
    record_type: Optional[str] = Form("general")
):
    """
    Endpoint for uploading generic clinical notes, PDFs, or secondary scans
    for ingestion into the vector database.
    patient_id and record_type are optional with sensible defaults.
    """
    try:
        saved_path = await file_handler.save_upload_file(file)
        
        return {
            "status": "success",
            "message": f"Successfully uploaded {record_type} record" + (f" for patient {patient_id}" if patient_id else ""),
            "file_path": saved_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
