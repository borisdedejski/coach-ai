from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import JournalEntry

async def get_last_journal_entries(db: AsyncSession, user_id: str, limit: int = 3):
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()
