from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from typing import List, Dict, Union

class MoodResponse(BaseModel):
    mood: str
    sentiment_score: float
    reflection_question: str
    progress_summary: Optional[str] = None
    progress_score: Optional[float] = None


class ChatResponse(BaseModel):
    reply: str
    intent: str
    mood: Optional[str] = None
    sentiment_score: Optional[float] = None
    reflection_question: Optional[str] = None
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


class InsightsResponse(BaseModel):
    average_sentiment_score: float
    most_common_mood: str
    mood_trend: str
    entry_streak_days: int
    total_entries: int
    last_entry_date: Optional[datetime]
    progress_trend: List[Dict[str, Union[str, float]]]
