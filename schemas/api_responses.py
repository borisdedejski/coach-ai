from pydantic import BaseModel

class MoodResponse(BaseModel):
    mood: str
    sentiment_score: float
    reflection_question: str
