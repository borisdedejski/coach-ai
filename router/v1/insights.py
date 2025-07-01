from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from collections import defaultdict
from datetime import datetime, timedelta
from db.session import get_db
from db.models import JournalEntry
from schemas.api_responses import InsightsResponse

router = APIRouter(tags=["insights"])

@router.get("/insights", status_code=status.HTTP_200_OK, response_model=InsightsResponse)
async def get_insights(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JournalEntry).where(JournalEntry.user_id == user_id).order_by(JournalEntry.timestamp.asc())
    )
    entries = result.scalars().all()

    if not entries:
        return InsightsResponse(
            average_sentiment_score=0.0,
            most_common_mood="none",
            mood_trend="none",
            entry_streak_days=0,
            total_entries=0,
            last_entry_date=None,
            progress_trend=[]
        )

    # Calculate average sentiment
    avg_sentiment = sum(e.sentiment_score for e in entries) / len(entries)

    # Most common mood
    mood_counts = defaultdict(int)
    for entry in entries:
        mood_counts[entry.mood] += 1
    most_common_mood = max(mood_counts.items(), key=lambda x: x[1])[0]

    # Mood trend (simple: compare first and last mood score)
    mood_trend = "stable"
    if len(entries) >= 2:
        first = entries[0].sentiment_score
        last = entries[-1].sentiment_score
        if last > first + 0.1:
            mood_trend = "improving"
        elif last < first - 0.1:
            mood_trend = "declining"

    # Entry streak (days in a row with entries)
    dates = {entry.timestamp.date() for entry in entries}
    today = datetime.utcnow().date()
    streak = 0
    for i in range(0, 30):  # max streak of 30 days
        day = today - timedelta(days=i)
        if day in dates:
            streak += 1
        else:
            break

    # Progress trend by date
    daily_scores = defaultdict(list)
    for entry in entries:
        if entry.progress_score is not None:
            day = entry.timestamp.date().isoformat()
            daily_scores[day].append(entry.progress_score)

    progress_trend = []
    for day, scores in sorted(daily_scores.items()):
        avg = sum(scores) / len(scores)
        progress_trend.append({
            "date": day,
            "progress_score": round(avg, 2)
        })

    return InsightsResponse(
        average_sentiment_score=round(avg_sentiment, 2),
        most_common_mood=most_common_mood,
        mood_trend=mood_trend,
        entry_streak_days=streak,
        total_entries=len(entries),
        last_entry_date=entries[-1].timestamp,
        progress_trend=progress_trend
    )
