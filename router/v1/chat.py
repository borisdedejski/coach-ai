from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models import JournalEntry
from agents.mood_tracker import analyze_mood
from schemas.api_requests import JournalEntryRequest
from schemas.api_responses import MoodResponse

router = APIRouter(tags=["chat"])

@router.post("/chat", status_code=status.HTTP_200_OK, response_model=MoodResponse)
async def stream_chat(entry: JournalEntryRequest, db: AsyncSession = Depends(get_db)):
    result = analyze_mood(entry.text)
    journal_entry = JournalEntry(
        user_id=entry.user_id,
        text=entry.text,
        mood=result["mood"],
        sentiment_score=result["sentiment_score"]
    )
    db.add(journal_entry)
    await db.commit()
    await db.refresh(journal_entry)

    return MoodResponse(mood=result["mood"], sentiment_score=result["sentiment_score"])
