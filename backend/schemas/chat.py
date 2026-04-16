from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    message: str
    patient_id: Optional[int] = None
    session_id: Optional[str] = None
