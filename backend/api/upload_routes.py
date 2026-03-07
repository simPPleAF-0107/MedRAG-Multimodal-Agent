from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.utils.file_handler import file_handler

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

@router.post("/record")
async def upload_record(
    patient_id: int = Form(...),
    record_type: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Endpoint for uploading generic clinical notes, PDFs, or secondary scans
    for ingestion into the vector database.
    """
    try:
        saved_path = await file_handler.save_upload_file(file)
        
        # Future: Trigger IngestAgent from here to parse, embed and store the file
        
        return {
            "status": "success",
            "message": f"Successfully uploaded {record_type} for patient {patient_id}",
            "file_path": saved_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
