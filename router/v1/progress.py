from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from agents.progress_agent import get_progress_summary
from schemas.api_responses import EnhancedProgressResponse

router = APIRouter(tags=["progress"])

@router.get("/progress/{user_id}", status_code=status.HTTP_200_OK, response_model=EnhancedProgressResponse)
async def progress(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await get_progress_summary(db, user_id)
    return EnhancedProgressResponse(**result)

@router.get("/progress/{user_id}/enhanced", status_code=status.HTTP_200_OK, response_model=EnhancedProgressResponse)
async def enhanced_progress(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get enhanced progress analysis with detailed patterns and trends"""
    result = await get_progress_summary(db, user_id)
    return EnhancedProgressResponse(**result)
