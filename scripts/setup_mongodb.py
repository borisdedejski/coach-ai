#!/usr/bin/env python3
"""
Setup script for MongoDB integration
This script helps set up MongoDB for the coach-ai application
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import json

async def setup_mongodb():
    """Set up MongoDB database and collections"""
    
    # Get MongoDB configuration
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("MONGODB_DATABASE", "coach_ai")
    
    print(f"🔧 Setting up MongoDB...")
    print(f"   URL: {mongodb_url}")
    print(f"   Database: {database_name}")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        database = client[database_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Create collections and indexes
        conversations_collection = database.conversations
        
        # Create indexes for better performance
        print("📊 Creating indexes...")
        
        # Index on user_id and timestamp
        await conversations_collection.create_index([
            ("user_id", 1),
            ("created_at", -1)
        ])
        print("   ✅ Created index on user_id and created_at")
        
        # Index on session_id
        await conversations_collection.create_index("session_id")
        print("   ✅ Created index on session_id")
        
        # Index on mood for analytics
        await conversations_collection.create_index("mood")
        print("   ✅ Created index on mood")
        
        # Index on sentiment_score for range queries
        await conversations_collection.create_index("sentiment_score")
        print("   ✅ Created index on sentiment_score")
        
        print("🎉 MongoDB setup completed successfully!")
        
        # Show some stats
        stats = await database.command("dbStats")
        print(f"📈 Database stats:")
        print(f"   Collections: {stats.get('collections', 0)}")
        print(f"   Data size: {stats.get('dataSize', 0)} bytes")
        print(f"   Storage size: {stats.get('storageSize', 0)} bytes")
        
    except Exception as e:
        print(f"❌ Error setting up MongoDB: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Make sure MongoDB is running: brew services start mongodb-community")
        print("   2. Check your MONGODB_URL environment variable")
        print("   3. Ensure you have the correct permissions")
        raise
    
    finally:
        client.close()

def create_sample_data():
    """Create sample conversation data for testing"""
    print("\n📝 Creating sample conversation data...")
    
    sample_conversation = {
        "user_id": "test_user",
        "session_id": "sample_session_001",
        "messages": [
            {
                "role": "user",
                "content": "I'm feeling anxious about my presentation tomorrow",
                "timestamp": "2024-01-15T10:00:00Z"
            },
            {
                "role": "assistant",
                "content": "I understand that presentations can feel overwhelming. Let's work through this together. What specifically about the presentation is making you feel anxious?",
                "timestamp": "2024-01-15T10:00:30Z",
                "metadata": {
                    "mood": "anxious",
                    "sentiment_score": -0.3,
                    "intent": "mood_entry"
                }
            }
        ],
        "mood": "anxious",
        "sentiment_score": -0.3,
        "intent": "mood_entry",
        "reflection_question": "What coping strategies have worked for you in similar situations?",
        "progress_summary": "User is experiencing presentation anxiety, showing awareness of emotional state",
        "progress_score": 0.6,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:30Z"
    }
    
    # Save sample data to file
    with open("sample_conversation.json", "w") as f:
        json.dump(sample_conversation, f, indent=2)
    
    print("✅ Sample conversation data saved to sample_conversation.json")
    print("   You can import this data using MongoDB Compass or mongoimport")

def main():
    """Main setup function"""
    print("🚀 Coach AI - MongoDB Setup")
    print("=" * 40)
    
    # Check environment variables
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    print(f"Using MongoDB URL: {mongodb_url}")
    
    # Run async setup
    asyncio.run(setup_mongodb())
    
    # Create sample data
    create_sample_data()
    
    print("\n🎯 Next steps:")
    print("   1. Set up your .env file with MONGODB_URL and MONGODB_DATABASE")
    print("   2. Run the database migration: alembic upgrade head")
    print("   3. Start the application: python main.py")
    print("   4. Test the new conversation endpoints")

if __name__ == "__main__":
    main()
