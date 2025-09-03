"""
Pydantic schemas for habit tracking
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class HabitResponse(BaseModel):
    id: Optional[int] = None
    user_habit_id: Optional[int] = None
    name: str
    category: str
    description: str
    frequency: str
    target_value: Optional[float] = None
    unit: Optional[str] = None
    reminder_time: Optional[str] = None
    mental_health_benefit: str

class UserHabitRequest(BaseModel):
    habit_id: int
    target_value: Optional[float] = None
    reminder_time: Optional[str] = None

class ActivityLogRequest(BaseModel):
    habit_id: int
    value: Optional[float] = None
    completed: bool = True
    notes: Optional[str] = None
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None

class ProgressData(BaseModel):
    completion_rate: float
    completed_days: int
    total_days: int
    current_streak: int
    longest_streak: int
    target_value: Optional[float] = None
    unit: Optional[str] = None

class ProgressResponse(BaseModel):
    user_id: str
    period_days: int
    progress: Dict[str, ProgressData]

class HabitRecommendationResponse(BaseModel):
    habit_name: str
    type: str  # "improvement" or "celebration"
    message: str
    suggestion: str

class UserPreferencesRequest(BaseModel):
    daily_checkin_enabled: Optional[bool] = None
    habit_reminders_enabled: Optional[bool] = None
    progress_notifications_enabled: Optional[bool] = None
    preferred_checkin_time: Optional[str] = None
    timezone: Optional[str] = None
    notification_frequency: Optional[str] = None

class UserPreferencesResponse(BaseModel):
    user_id: str
    daily_checkin_enabled: bool
    habit_reminders_enabled: bool
    progress_notifications_enabled: bool
    preferred_checkin_time: str
    timezone: str
    notification_frequency: str
    created_at: datetime
    updated_at: datetime 