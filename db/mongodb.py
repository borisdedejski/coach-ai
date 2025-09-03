import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
import asyncio

class MongoDBConnection:
    """MongoDB connection manager for async operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.conversations_collection = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            # Get MongoDB URL from environment or use default
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            database_name = os.getenv("MONGODB_DATABASE", "coach_ai")
            
            self.client = AsyncIOMotorClient(mongodb_url)
            self.database = self.client[database_name]
            self.conversations_collection = self.database.conversations
            
            # Test the connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {database_name}")
            
            # Create indexes for better performance
            await self._create_indexes()
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Index on user_id and timestamp for efficient queries
            await self.conversations_collection.create_index([
                ("user_id", 1),
                ("timestamp", -1)
            ])
            
            # Index on session_id for session-based queries
            await self.conversations_collection.create_index("session_id")
            
            # Index on mood for mood-based analytics
            await self.conversations_collection.create_index("mood")
            
            print("✅ MongoDB indexes created successfully")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes: {e}")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        return self.database[collection_name]

# Global MongoDB connection instance
mongodb_connection = MongoDBConnection()

async def get_mongodb():
    """Dependency to get MongoDB connection"""
    if not mongodb_connection.client:
        await mongodb_connection.connect()
    return mongodb_connection

async def get_conversations_collection():
    """Get the conversations collection"""
    mongodb = await get_mongodb()
    return mongodb.conversations_collection
