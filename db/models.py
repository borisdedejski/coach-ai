from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ConversationSummary(Base):
    """Store conversation summaries instead of full conversations"""
    __tablename__ = "conversation_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, index=True)
    conversation_count = Column(Integer, default=0)
    mood_summary = Column(String, nullable=True)
    avg_sentiment = Column(Float, nullable=True)
    key_topics = Column(JSON, nullable=True)  # Store as JSON array
    last_message_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserMemory(Base):
    """Store user memory and conversation context for quick access"""
    __tablename__ = "user_memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    current_mood_trend = Column(String, nullable=True)
    recent_moods = Column(JSON, nullable=True)  # Store as JSON array
    avg_sentiment = Column(Float, nullable=True)
    total_conversations = Column(Integer, default=0)
    last_conversation_at = Column(DateTime, nullable=True)
    progress_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Keep JournalEntry for backward compatibility during migration
class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    text = Column(String)
    mood = Column(String)
    sentiment_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    reflection_question = Column(String, nullable=True)
    progress_summary = Column(String, nullable=True)
    progress_score = Column(Float, nullable=True)

class Habit(Base):
    """Define available habits that users can track"""
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)  # e.g., 'sleep', 'exercise', 'mindfulness', 'social', 'work'
    description = Column(Text)
    frequency = Column(String)  # e.g., 'daily', 'weekly', 'custom'
    target_value = Column(Float, nullable=True)  # e.g., 8 hours for sleep, 30 minutes for exercise
    unit = Column(String, nullable=True)  # e.g., 'hours', 'minutes', 'times'
    mental_health_benefit = Column(Text)
    is_active = Column(Boolean, default=True)

class UserHabit(Base):
    """User's personal habit tracking preferences"""
    __tablename__ = "user_habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    habit_id = Column(Integer, index=True)
    is_active = Column(Boolean, default=True)
    target_value = Column(Float, nullable=True)  # User's personal target
    reminder_time = Column(String, nullable=True)  # e.g., "09:00", "18:00"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActivityLog(Base):
    """Track user's daily activities and habit completion"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    habit_id = Column(Integer, index=True)
    activity_date = Column(DateTime, default=datetime.utcnow)
    value = Column(Float, nullable=True)  # Actual value achieved
    completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    mood_before = Column(String, nullable=True)
    mood_after = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class HabitStreak(Base):
    """Track user's habit streaks for motivation"""
    __tablename__ = "habit_streaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    habit_id = Column(Integer, index=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_completed_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserPreferences(Base):
    """User preferences for proactive features"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    daily_checkin_enabled = Column(Boolean, default=True)
    habit_reminders_enabled = Column(Boolean, default=True)
    progress_notifications_enabled = Column(Boolean, default=True)
    preferred_checkin_time = Column(String, default="09:00")  # HH:MM format
    timezone = Column(String, default="UTC")
    notification_frequency = Column(String, default="daily")  # daily, weekly, custom
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
