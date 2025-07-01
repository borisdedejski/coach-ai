from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models import JournalEntry
from schemas.api_responses import JournalEntryResponse
from typing import List

router = APIRouter(tags=["history"])


@router.get("/history", response_model=List[JournalEntryResponse])
async def get_history(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        JournalEntry.__table__.select()
        .where(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.timestamp.desc())
        .limit(limit)
    )
    entries = result.fetchall()
    return [JournalEntryResponse.from_orm(row) for row in entries]