from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from agents.progress_agent import get_progress_summary

router = APIRouter(tags=["progress"])

@router.get("/progress/{user_id}")
async def progress(user_id: str, db: AsyncSession = Depends(get_db)):
    return await get_progress_summary(db, user_id)
