"""
Habit & Activity Tracking Service
Provides proactive habit management and tracking capabilities
"""
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func, select

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from db.models import Habit, UserHabit, ActivityLog, HabitStreak, UserPreferences
from db.session import get_db

class HabitService:
    """Service for managing habits and activity tracking"""
    
    def __init__(self):
        self.default_habits = [
            {
                "name": "Sleep Quality",
                "category": "sleep",
                "description": "Track your sleep duration and quality",
                "frequency": "daily",
                "target_value": 8.0,
                "unit": "hours",
                "mental_health_benefit": "Good sleep improves mood, reduces anxiety, and enhances cognitive function."
            },
            {
                "name": "Exercise",
                "category": "exercise",
                "description": "Physical activity for mental health",
                "frequency": "daily",
                "target_value": 30.0,
                "unit": "minutes",
                "mental_health_benefit": "Exercise releases endorphins, reduces stress, and improves overall mood."
            },
            {
                "name": "Meditation",
                "category": "mindfulness",
                "description": "Mindfulness and meditation practice",
                "frequency": "daily",
                "target_value": 10.0,
                "unit": "minutes",
                "mental_health_benefit": "Meditation reduces stress, improves focus, and promotes emotional balance."
            },
            {
                "name": "Social Connection",
                "category": "social",
                "description": "Meaningful social interactions",
                "frequency": "daily",
                "target_value": 1.0,
                "unit": "interactions",
                "mental_health_benefit": "Social connections reduce loneliness and improve emotional well-being."
            },
            {
                "name": "Gratitude Practice",
                "category": "mindfulness",
                "description": "Daily gratitude journaling or reflection",
                "frequency": "daily",
                "target_value": 3.0,
                "unit": "items",
                "mental_health_benefit": "Gratitude practice increases positive emotions and life satisfaction."
            },
            {
                "name": "Water Intake",
                "category": "health",
                "description": "Track daily water consumption",
                "frequency": "daily",
                "target_value": 8.0,
                "unit": "glasses",
                "mental_health_benefit": "Proper hydration improves cognitive function and reduces fatigue."
            },
            {
                "name": "Reading",
                "category": "learning",
                "description": "Daily reading for personal growth",
                "frequency": "daily",
                "target_value": 20.0,
                "unit": "minutes",
                "mental_health_benefit": "Reading reduces stress, improves focus, and expands knowledge."
            },
            {
                "name": "Nature Time",
                "category": "wellness",
                "description": "Time spent outdoors in nature",
                "frequency": "daily",
                "target_value": 15.0,
                "unit": "minutes",
                "mental_health_benefit": "Nature exposure reduces stress, improves mood, and enhances creativity."
            }
        ]
    
    async def initialize_default_habits(self, db: AsyncSession) -> List[Habit]:
        """Initialize default habits in the database"""
        habits = []
        for habit_data in self.default_habits:
            result = await db.execute(
                select(Habit).where(Habit.name == habit_data["name"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                habit = Habit(**habit_data)
                db.add(habit)
                habits.append(habit)
        
        await db.commit()
        return habits
    
    async def get_available_habits(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get all available habits"""
        result = await db.execute(
            select(Habit).where(Habit.is_active == True)
        )
        habits = result.scalars().all()
        
        return [
            {
                "id": habit.id,
                "name": habit.name,
                "category": habit.category,
                "description": habit.description,
                "frequency": habit.frequency,
                "target_value": habit.target_value,
                "unit": habit.unit,
                "mental_health_benefit": habit.mental_health_benefit
            }
            for habit in habits
        ]
    
    async def get_user_habits(self, db: AsyncSession, user_id: str) -> List[Dict[str, Any]]:
        """Get user's active habits"""
        result = await db.execute(
            select(UserHabit, Habit)
            .join(Habit)
            .where(
                and_(
                    UserHabit.user_id == user_id,
                    UserHabit.is_active == True
                )
            )
        )
        user_habits = result.all()
        
        return [
            {
                "user_habit_id": uh.id,
                "habit_id": h.id,
                "name": h.name,
                "category": h.category,
                "description": h.description,
                "target_value": uh.target_value or h.target_value,
                "unit": h.unit,
                "reminder_time": uh.reminder_time,
                "mental_health_benefit": h.mental_health_benefit
            }
            for uh, h in user_habits
        ]
    
    async def add_user_habit(self, db: AsyncSession, user_id: str, habit_id: int, 
                      target_value: Optional[float] = None, 
                      reminder_time: Optional[str] = None) -> UserHabit:
        """Add a habit for a user"""
        # Check if habit already exists for user
        result = await db.execute(
            select(UserHabit).where(
                and_(
                    UserHabit.user_id == user_id,
                    UserHabit.habit_id == habit_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing habit
            if target_value is not None:
                existing.target_value = target_value
            if reminder_time is not None:
                existing.reminder_time = reminder_time
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            await db.commit()
            return existing
        
        # Create new user habit
        user_habit = UserHabit(
            user_id=user_id,
            habit_id=habit_id,
            target_value=target_value,
            reminder_time=reminder_time
        )
        db.add(user_habit)
        await db.commit()
        await db.refresh(user_habit)
        
        # Initialize streak tracking
        streak = HabitStreak(
            user_id=user_id,
            habit_id=habit_id
        )
        db.add(streak)
        await db.commit()
        
        return user_habit
    
    async def log_activity(self, db: AsyncSession, user_id: str, habit_id: int, 
                    value: Optional[float] = None, completed: bool = True,
                    notes: Optional[str] = None, mood_before: Optional[str] = None,
                    mood_after: Optional[str] = None) -> ActivityLog:
        """Log a user's activity for a habit"""
        activity = ActivityLog(
            user_id=user_id,
            habit_id=habit_id,
            value=value,
            completed=completed,
            notes=notes,
            mood_before=mood_before,
            mood_after=mood_after
        )
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
        
        # Update streak if completed
        if completed:
            await self._update_streak(db, user_id, habit_id)
        
        return activity
    
    async def _update_streak(self, db: AsyncSession, user_id: str, habit_id: int):
        """Update user's habit streak"""
        result = await db.execute(
            select(HabitStreak).where(
                and_(
                    HabitStreak.user_id == user_id,
                    HabitStreak.habit_id == habit_id
                )
            )
        )
        streak = result.scalar_one_or_none()
        
        if not streak:
            return
        
        today = datetime.utcnow().date()
        
        if streak.last_completed_date:
            last_date = streak.last_completed_date.date()
            if today == last_date:
                # Already logged today
                return
            elif today - last_date == timedelta(days=1):
                # Consecutive day
                streak.current_streak += 1
            else:
                # Streak broken
                streak.current_streak = 1
        else:
            # First completion
            streak.current_streak = 1
        
        streak.last_completed_date = datetime.utcnow()
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.updated_at = datetime.utcnow()
        
        await db.commit()
    
    async def get_user_progress(self, db: AsyncSession, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get user's habit progress over the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user's active habits
        user_habits = await self.get_user_habits(db, user_id)
        
        progress = {}
        for habit in user_habits:
            habit_id = habit["habit_id"]
            
            # Get activity logs for this habit
            result = await db.execute(
                select(ActivityLog).where(
                    and_(
                        ActivityLog.user_id == user_id,
                        ActivityLog.habit_id == habit_id,
                        ActivityLog.activity_date >= start_date
                    )
                )
            )
            activities = result.scalars().all()
            
            # Calculate completion rate
            total_days = days
            completed_days = len([a for a in activities if a.completed])
            completion_rate = (completed_days / total_days) * 100 if total_days > 0 else 0
            
            # Get current streak
            result = await db.execute(
                select(HabitStreak).where(
                    and_(
                        HabitStreak.user_id == user_id,
                        HabitStreak.habit_id == habit_id
                    )
                )
            )
            streak = result.scalar_one_or_none()
            
            progress[habit["name"]] = {
                "completion_rate": round(completion_rate, 1),
                "completed_days": completed_days,
                "total_days": total_days,
                "current_streak": streak.current_streak if streak else 0,
                "longest_streak": streak.longest_streak if streak else 0,
                "target_value": habit["target_value"],
                "unit": habit["unit"]
            }
        
        return progress
    
    async def get_daily_checkin_prompt(self, db: AsyncSession, user_id: str) -> str:
        """Get personalized daily check-in prompt based on user's habits and progress"""
        progress = await self.get_user_progress(db, user_id, days=7)
        user_habits = await self.get_user_habits(db, user_id)
        
        if not user_habits:
            return "Hello! I'm here to support your mental well-being journey. How are you feeling today? Share your thoughts, emotions, or any challenges you're facing."
        
        # Find habits that need attention
        struggling_habits = []
        excelling_habits = []
        
        for habit in user_habits:
            habit_name = habit["name"]
            if habit_name in progress:
                data = progress[habit_name]
                if data["completion_rate"] < 30:
                    struggling_habits.append(habit_name)
                elif data["current_streak"] >= 5:
                    excelling_habits.append(habit_name)
        
        # Build personalized prompt
        prompt = "Hello! How are you feeling today? "
        
        if struggling_habits:
            prompt += f"I noticed you've been having trouble with {', '.join(struggling_habits)}. "
            prompt += "Remember, it's okay to have off days. What's been challenging? "
        
        if excelling_habits:
            prompt += f"Great job maintaining {', '.join(excelling_habits)}! "
            prompt += "How has this been helping your mood? "
        
        if not struggling_habits and not excelling_habits:
            prompt += "How has your day been so far? Any particular emotions or experiences you'd like to share? "
        
        return prompt
    
    async def get_habit_recommendations(self, db: AsyncSession, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized habit recommendations based on user's progress"""
        progress = await self.get_user_progress(db, user_id, days=7)
        user_habits = await self.get_user_habits(db, user_id)
        
        recommendations = []
        
        for habit in user_habits:
            habit_name = habit["name"]
            if habit_name in progress:
                data = progress[habit_name]
                
                if data["completion_rate"] < 30:
                    recommendations.append({
                        "habit_name": habit_name,
                        "type": "improvement",
                        "message": f"Let's work on {habit_name}. You've completed it {data['completed_days']} out of 7 days.",
                        "suggestion": f"Try setting a smaller goal for {habit_name} to build momentum."
                    })
                elif data["current_streak"] >= 5:
                    recommendations.append({
                        "habit_name": habit_name,
                        "type": "celebration",
                        "message": f"Amazing! You've maintained {habit_name} for {data['current_streak']} days!",
                        "suggestion": "Keep up the great work! Consider adding another habit to your routine."
                    })
        
        return recommendations
    
    async def get_user_preferences(self, db: AsyncSession, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences for proactive features"""
        result = await db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user_preferences(self, db: AsyncSession, user_id: str, **kwargs) -> UserPreferences:
        """Update user preferences"""
        prefs = await self.get_user_preferences(db, user_id)
        
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.add(prefs)
        
        for key, value in kwargs.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        
        prefs.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(prefs)
        
        return prefs 