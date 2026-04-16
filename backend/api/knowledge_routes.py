from fastapi import APIRouter
from backend.services.knowledge_gap_tracker import get_all_gaps, mark_gap_seeded

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/knowledge-gaps")
async def list_knowledge_gaps():
    """Returns all logged knowledge gaps (recent first)."""
    return {"knowledge_gaps": get_all_gaps()}

@router.post("/knowledge-gaps/mark-seeded")
async def mark_knowledge_gap_seeded(query_prefix: str):
    """Marks gaps starting with query_prefix as seeded."""
    count = mark_gap_seeded(query_prefix)
    return {"message": f"Updated {count} records to 'seeded'."}
