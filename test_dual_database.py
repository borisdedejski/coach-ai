#!/usr/bin/env python3
"""
Test script for the dual-database system
This script tests both MongoDB and PostgreSQL integration
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.mongodb import mongodb_connection
from db.mongodb_crud import ConversationCRUD
from db.conversation_crud import ConversationSummaryCRUD, UserMemoryCRUD
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("🔍 Testing MongoDB connection...")
    
    try:
        await mongodb_connection.connect()
        conversations_collection = mongodb_connection.conversations_collection
        conversation_crud = ConversationCRUD(conversations_collection)
        
        # Test creating a conversation
        conversation_id = await conversation_crud.create_conversation(
            user_id="test_user",
            session_id="test_session_001",
            user_message="I'm feeling anxious about my presentation tomorrow",
            assistant_reply="I understand that presentations can feel overwhelming. Let's work through this together.",
            mood="anxious",
            sentiment_score=-0.3,
            intent="mood_entry",
            reflection_question="What coping strategies have worked for you in similar situations?",
            progress_summary="User is experiencing presentation anxiety",
            progress_score=0.6
        )
        
        print(f"✅ Created conversation with ID: {conversation_id}")
        
        # Test retrieving conversations
        conversations = await conversation_crud.get_user_conversations(
            user_id="test_user",
            limit=5
        )
        
        print(f"✅ Retrieved {len(conversations)} conversations")
        
        # Test getting recent messages
        recent_messages = await conversation_crud.get_user_recent_messages(
            user_id="test_user",
            limit=3
        )
        
        print(f"✅ Retrieved {len(recent_messages)} recent messages")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False

async def test_postgresql_operations():
    """Test PostgreSQL operations"""
    print("\n🔍 Testing PostgreSQL operations...")
    
    try:
        # Get database session
        async for db in get_db():
            summary_crud = ConversationSummaryCRUD()
            memory_crud = UserMemoryCRUD()
            
            # Test creating conversation summary
            summary = await summary_crud.create_conversation_summary(
                db=db,
                user_id="test_user",
                session_id="test_session_001",
                conversation_count=2,
                mood_summary="anxious",
                avg_sentiment=-0.3,
                key_topics=["anxiety", "presentation"]
            )
            
            print(f"✅ Created conversation summary with ID: {summary.id}")
            
            # Test creating/updating user memory
            memory = await memory_crud.create_or_update_user_memory(
                db=db,
                user_id="test_user",
                current_mood_trend="anxious",
                recent_moods=["anxious", "worried"],
                avg_sentiment=-0.3,
                total_conversations=1,
                progress_summary="User is working through presentation anxiety"
            )
            
            print(f"✅ Created/updated user memory for user: {memory.user_id}")
            
            # Test retrieving user memory
            retrieved_memory = await memory_crud.get_user_memory(db=db, user_id="test_user")
            
            if retrieved_memory:
                print(f"✅ Retrieved user memory: {retrieved_memory.current_mood_trend}")
            else:
                print("❌ Failed to retrieve user memory")
                return False
            
            break  # Exit the async generator
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL test failed: {e}")
        return False

async def test_integration():
    """Test the full integration"""
    print("\n🔍 Testing full integration...")
    
    try:
        # Test MongoDB
        mongodb_success = await test_mongodb_connection()
        
        # Test PostgreSQL
        postgresql_success = await test_postgresql_operations()
        
        if mongodb_success and postgresql_success:
            print("\n🎉 All tests passed! Dual-database system is working correctly.")
            return True
        else:
            print("\n❌ Some tests failed. Check the errors above.")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    finally:
        # Clean up
        await mongodb_connection.disconnect()

async def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        await mongodb_connection.connect()
        conversations_collection = mongodb_connection.conversations_collection
        
        # Delete test conversations
        result = await conversations_collection.delete_many({"user_id": "test_user"})
        print(f"✅ Deleted {result.deleted_count} test conversations from MongoDB")
        
        # Clean up PostgreSQL test data
        async for db in get_db():
            from db.models import ConversationSummary, UserMemory
            
            # Delete test summaries
            await db.execute(
                "DELETE FROM conversation_summaries WHERE user_id = 'test_user'"
            )
            
            # Delete test memory
            await db.execute(
                "DELETE FROM user_memories WHERE user_id = 'test_user'"
            )
            
            await db.commit()
            print("✅ Cleaned up test data from PostgreSQL")
            break
        
    except Exception as e:
        print(f"⚠️  Cleanup failed: {e}")
    
    finally:
        await mongodb_connection.disconnect()

async def main():
    """Main test function"""
    print("🚀 Coach AI - Dual Database Integration Test")
    print("=" * 50)
    
    # Check environment variables
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_url = os.getenv("DATABASE_URL")
    
    print(f"MongoDB URL: {mongodb_url}")
    print(f"Database URL: {'Set' if database_url else 'Not set'}")
    
    if not database_url:
        print("❌ DATABASE_URL not set. Please check your .env file.")
        return
    
    # Run tests
    success = await test_integration()
    
    if success:
        # Ask if user wants to clean up test data
        cleanup = input("\n🧹 Clean up test data? (y/n): ").lower().strip()
        if cleanup == 'y':
            await cleanup_test_data()
    
    print("\n✨ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())


