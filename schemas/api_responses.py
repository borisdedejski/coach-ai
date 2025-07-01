from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class MoodResponse(BaseModel):
    mood: str
    sentiment_score: float
    reflection_question: str
    progress_summary: Optional[str] = None
    progress_score: Optional[float] = None


class JournalEntryResponse(BaseModel):
    id: int
    user_id: str
    text: str
    mood: str
    sentiment_score: float
    timestamp: datetime
    reflection_question: Optional[str] = None
    progress_summary: Optional[str] = None
    progress_score: Optional[float] = None

    class Config:
        from_attributes = True
