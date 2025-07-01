from sqlalchemy import select, desc
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from agents.reflection_agent import get_reflection_question
from db.session import get_db
from db.models import JournalEntry
from agents.mood_tracker import analyze_mood
from schemas.api_requests import JournalEntryRequest
from schemas.api_responses import MoodResponse
from agents.progress_agent import get_progress_summary

router = APIRouter(tags=["chat"])

@router.post("/chat", status_code=status.HTTP_200_OK, response_model=MoodResponse)
async def stream_chat(entry: JournalEntryRequest, db: AsyncSession = Depends(get_db)):
    result = analyze_mood(entry.text)

    reflection_question = await get_reflection_question(db, entry.user_id, result["mood"])

    progress_data = await get_progress_summary(db, entry.user_id)
    summary = progress_data.get("summary")
    score = progress_data.get("score")

    journal_entry = JournalEntry(
        user_id=entry.user_id,
        text=entry.text,
        mood=result["mood"],
        sentiment_score=result["sentiment_score"],
        reflection_question=reflection_question,
        progress_summary=summary,
        progress_score=score,
    )

    db.add(journal_entry)
    await db.commit()
    await db.refresh(journal_entry)

    return MoodResponse(
        mood=result["mood"],
        sentiment_score=result["sentiment_score"],
        reflection_question=reflection_question,
        progress_summary=summary,
        progress_score=score,
    )
