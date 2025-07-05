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
    # RAG metadata
    used_knowledge_base: Optional[bool] = None
    similarity_score: Optional[float] = None
    knowledge_context: Optional[str] = None


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


class ProgressPatternsResponse(BaseModel):
    day_patterns: Dict[str, Dict[str, Union[str, float, int]]]
    trend_analysis: Dict[str, Union[str, float]]
    trigger_analysis: Dict[str, Union[List[str], Dict[str, int], int]]
    mood_direction: Dict[str, Union[str, float]]


class EnhancedProgressResponse(BaseModel):
    summary: Optional[str] = None
    score: Optional[float] = None
    patterns: Optional[ProgressPatternsResponse] = None


class InsightsResponse(BaseModel):
    average_sentiment_score: float
    most_common_mood: str
    mood_trend: str
    entry_streak_days: int
    total_entries: int
    last_entry_date: Optional[datetime]
    progress_trend: List[Dict[str, Union[str, float]]]
