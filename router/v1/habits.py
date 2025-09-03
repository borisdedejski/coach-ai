"""
Habit & Activity Tracking API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import datetime

from db.session import get_db
from service.habit_service import HabitService
from schemas.habit_schemas import (
    HabitResponse, UserHabitRequest, ActivityLogRequest, 
    ProgressResponse, HabitRecommendationResponse
)

router = APIRouter(prefix="/habits", tags=["habits"])

habit_service = HabitService()

@router.get("/available", response_model=List[HabitResponse])
async def get_available_habits(db: AsyncSession = Depends(get_db)):
    """Get all available habits that users can track"""
    try:
        habits = await habit_service.get_available_habits(db)
        return habits
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available habits: {str(e)}"
        )

@router.get("/my-habits", response_model=List[HabitResponse])
async def get_user_habits(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user's active habits"""
    try:
        habits = await habit_service.get_user_habits(db, user_id)
        return habits
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user habits: {str(e)}"
        )

@router.post("/add-habit")
async def add_user_habit(
    user_id: str, 
    habit_id: int, 
    target_value: Optional[float] = None,
    reminder_time: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Add a habit for a user to track"""
    try:
        user_habit = await habit_service.add_user_habit(
            db, user_id, habit_id, target_value, reminder_time
        )
        return {
            "message": "Habit added successfully",
            "user_habit_id": user_habit.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add habit: {str(e)}"
        )

@router.post("/log-activity")
async def log_activity(
    user_id: str,
    habit_id: int,
    value: Optional[float] = None,
    completed: bool = True,
    notes: Optional[str] = None,
    mood_before: Optional[str] = None,
    mood_after: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Log a user's activity for a habit"""
    try:
        activity = await habit_service.log_activity(
            db, user_id, habit_id, value, completed, notes, mood_before, mood_after
        )
        return {
            "message": "Activity logged successfully",
            "activity_id": activity.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log activity: {str(e)}"
        )

@router.get("/progress", response_model=ProgressResponse)
async def get_user_progress(
    user_id: str, 
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get user's habit progress over the last N days"""
    try:
        progress = await habit_service.get_user_progress(db, user_id, days)
        return {
            "user_id": user_id,
            "period_days": days,
            "progress": progress
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )

@router.get("/recommendations", response_model=List[HabitRecommendationResponse])
async def get_habit_recommendations(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get personalized habit recommendations"""
    try:
        recommendations = await habit_service.get_habit_recommendations(db, user_id)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )

@router.get("/daily-checkin")
async def get_daily_checkin_prompt(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get personalized daily check-in prompt"""
    try:
        prompt = await habit_service.get_daily_checkin_prompt(db, user_id)
        return {
            "user_id": user_id,
            "prompt": prompt,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get check-in prompt: {str(e)}"
        )

@router.post("/initialize")
async def initialize_habits(db: AsyncSession = Depends(get_db)):
    """Initialize default habits in the database (admin only)"""
    try:
        habits = await habit_service.initialize_default_habits(db)
        return {
            "message": f"Initialized {len(habits)} default habits",
            "habits_created": len(habits)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize habits: {str(e)}"
        ) 