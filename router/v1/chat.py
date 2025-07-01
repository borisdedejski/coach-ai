from sqlalchemy import select, desc
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from agents.reflection_agent import get_reflection_question
from db.session import get_db
from db.models import JournalEntry
from agents.mood_tracker import analyze_mood
from schemas.api_requests import JournalEntryRequest
from schemas.api_responses import MoodResponse

router = APIRouter(tags=["chat"])

@router.post("/chat", status_code=status.HTTP_200_OK, response_model=MoodResponse)
async def stream_chat(entry: JournalEntryRequest, db: AsyncSession = Depends(get_db)):
    # Analyze mood from current journal entry
    result = analyze_mood(entry.text)


    reflection = await get_reflection_question(db, user_id=entry.user_id, mood=result["mood"])

    # Save journal entry including reflection
    journal_entry = JournalEntry(
        user_id=entry.user_id,
        text=entry.text,
        mood=result["mood"],
        sentiment_score=result["sentiment_score"],
        reflection_question=reflection
    )
    db.add(journal_entry)
    await db.commit()
    await db.refresh(journal_entry)

    # Return full response
    return MoodResponse(
        mood=result["mood"],
        sentiment_score=result["sentiment_score"],
        reflection_question=reflection,
    )
