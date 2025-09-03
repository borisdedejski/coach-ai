#!/usr/bin/env python3
"""
Create habit tracking tables in the database
"""
import os
import sys
import asyncio
from sqlalchemy import create_engine, text

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from db.models import Base, Habit, UserHabit, ActivityLog, HabitStreak, UserPreferences
from db.session import get_db
from service.habit_service import HabitService

async def create_habit_tables():
    """Create all habit-related tables"""
    print("🔧 Creating habit tracking tables...")
    
    try:
        # Get database URL from environment or use default
        database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/coach_ai")
        engine = create_engine(database_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Habit tables created successfully!")
        
        # Initialize default habits
        print("📝 Initializing default habits...")
        async for db in get_db():
            habit_service = HabitService()
            habits = await habit_service.initialize_default_habits(db)
            print(f"✅ Initialized {len(habits)} default habits")
            break
        
        print("🎉 Habit tracking system setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating habit tables: {e}")
        return False

def verify_tables():
    """Verify that all tables were created correctly"""
    print("🔍 Verifying tables...")
    
    try:
        with next(get_db()) as db:
            # Check if tables exist
            tables = ["habits", "user_habits", "activity_logs", "habit_streaks", "user_preferences"]
            
            for table in tables:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"   ✅ {table}: {count} records")
            
            # Check default habits
            result = db.execute(text("SELECT COUNT(*) FROM habits"))
            habit_count = result.scalar()
            print(f"   📊 Total habits available: {habit_count}")
            
        print("✅ All tables verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Setting up Habit Tracking System")
    print("=" * 40)
    
    # Create tables
    if not asyncio.run(create_habit_tables()):
        print("❌ Failed to create tables")
        return False
    
    # Verify tables
    if not verify_tables():
        print("❌ Failed to verify tables")
        return False
    
    print("\n🎉 Habit tracking system is ready!")
    print("📋 Available API endpoints:")
    print("   GET  /v1/habits/available - Get all available habits")
    print("   GET  /v1/habits/my-habits - Get user's active habits")
    print("   POST /v1/habits/add-habit - Add a habit for user")
    print("   POST /v1/habits/log-activity - Log activity completion")
    print("   GET  /v1/habits/progress - Get user's progress")
    print("   GET  /v1/habits/recommendations - Get personalized recommendations")
    print("   GET  /v1/habits/daily-checkin - Get daily check-in prompt")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 