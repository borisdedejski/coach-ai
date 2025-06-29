from fastapi import APIRouter, status
from schemas.api_requests import JournalEntryRequest
from schemas.api_responses import MoodResponse

router = APIRouter(prefix="", tags=["chat"])

from agents.mood_tracker import analyze_mood

@router.post("/chat", status_code=status.HTTP_200_OK, response_model=MoodResponse)
async def stream_chat(entry: JournalEntryRequest):
    result = analyze_mood(entry.text)
    return MoodResponse(**result)
