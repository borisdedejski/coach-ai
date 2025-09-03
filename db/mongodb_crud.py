from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from db.mongodb_models import ConversationDocument, ConversationMessage, ConversationSummary
from bson import ObjectId
import json

class ConversationCRUD:
    """CRUD operations for MongoDB conversations"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create_conversation(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        assistant_reply: str,
        mood: Optional[str] = None,
        sentiment_score: Optional[float] = None,
        intent: Optional[str] = None,
        reflection_question: Optional[str] = None,
        progress_summary: Optional[str] = None,
        progress_score: Optional[float] = None,
        used_knowledge_base: Optional[bool] = None,
        similarity_score: Optional[float] = None,
        knowledge_context: Optional[str] = None
    ) -> str:
        """Create a new conversation with user and assistant messages"""
        
        # Create conversation messages
        messages = [
            ConversationMessage(
                role="user",
                content=user_message,
                timestamp=datetime.utcnow()
            ),
            ConversationMessage(
                role="assistant",
                content=assistant_reply,
                timestamp=datetime.utcnow(),
                metadata={
                    "mood": mood,
                    "sentiment_score": sentiment_score,
                    "intent": intent,
                    "reflection_question": reflection_question,
                    "progress_summary": progress_summary,
                    "progress_score": progress_score,
                    "used_knowledge_base": used_knowledge_base,
                    "similarity_score": similarity_score,
                    "knowledge_context": knowledge_context
                }
            )
        ]
        
        # Create conversation document
        conversation = ConversationDocument(
            user_id=user_id,
            session_id=session_id,
            messages=messages,
            mood=mood,
            sentiment_score=sentiment_score,
            intent=intent,
            reflection_question=reflection_question,
            progress_summary=progress_summary,
            progress_score=progress_score,
            used_knowledge_base=used_knowledge_base,
            similarity_score=similarity_score,
            knowledge_context=knowledge_context
        )
        
        # Insert into MongoDB
        result = await self.collection.insert_one(conversation.dict(by_alias=True))
        return str(result.inserted_id)
    
    async def add_message_to_conversation(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a message to an existing conversation"""
        try:
            message = ConversationMessage(
                role=role,
                content=content,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            result = await self.collection.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$push": {"messages": message.dict()},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding message to conversation: {e}")
            return False
    
    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 10,
        skip: int = 0
    ) -> List[ConversationDocument]:
        """Get user's recent conversations"""
        try:
            cursor = self.collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            conversations = []
            async for doc in cursor:
                conversations.append(ConversationDocument(**doc))
            
            return conversations
        except Exception as e:
            print(f"Error getting user conversations: {e}")
            return []
    
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[ConversationDocument]:
        """Get a specific conversation by ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(conversation_id)})
            if doc:
                return ConversationDocument(**doc)
            return None
        except Exception as e:
            print(f"Error getting conversation by ID: {e}")
            return None
    
    async def get_user_recent_messages(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get user's recent messages for context"""
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$sort": {"created_at": -1}},
                {"$limit": limit},
                {"$unwind": "$messages"},
                {"$sort": {"messages.timestamp": -1}},
                {"$limit": limit * 2},  # Get more messages since we're unwinding
                {"$project": {
                    "role": "$messages.role",
                    "content": "$messages.content",
                    "timestamp": "$messages.timestamp",
                    "mood": "$mood",
                    "sentiment_score": "$sentiment_score"
                }}
            ]
            
            messages = []
            async for doc in self.collection.aggregate(pipeline):
                messages.append(doc)
            
            return messages
        except Exception as e:
            print(f"Error getting user recent messages: {e}")
            return []
    
    async def get_user_mood_history(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get user's mood history for analysis"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "created_at": {"$gte": start_date},
                    "mood": {"$ne": None}
                }},
                {"$sort": {"created_at": -1}},
                {"$project": {
                    "mood": 1,
                    "sentiment_score": 1,
                    "created_at": 1,
                    "progress_score": 1
                }}
            ]
            
            moods = []
            async for doc in self.collection.aggregate(pipeline):
                moods.append(doc)
            
            return moods
        except Exception as e:
            print(f"Error getting user mood history: {e}")
            return []
    
    async def generate_conversation_summary(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[ConversationSummary]:
        """Generate a summary of a conversation for PostgreSQL storage"""
        try:
            # Get all conversations for this session
            conversations = await self.collection.find({
                "user_id": user_id,
                "session_id": session_id
            }).to_list(None)
            
            if not conversations:
                return None
            
            # Calculate summary statistics
            total_messages = sum(len(conv["messages"]) for conv in conversations)
            moods = [conv.get("mood") for conv in conversations if conv.get("mood")]
            sentiments = [conv.get("sentiment_score") for conv in conversations if conv.get("sentiment_score")]
            
            # Extract key topics (simplified - could be enhanced with NLP)
            key_topics = []
            for conv in conversations:
                for message in conv.get("messages", []):
                    if message["role"] == "user":
                        # Simple keyword extraction (could be enhanced)
                        content = message["content"].lower()
                        if any(word in content for word in ["anxiety", "stress", "worried"]):
                            key_topics.append("anxiety")
                        elif any(word in content for word in ["happy", "good", "great"]):
                            key_topics.append("positive_mood")
                        elif any(word in content for word in ["sad", "depressed", "down"]):
                            key_topics.append("sadness")
            
            # Remove duplicates and limit
            key_topics = list(set(key_topics))[:5]
            
            summary = ConversationSummary(
                user_id=user_id,
                session_id=session_id,
                conversation_count=total_messages,
                mood_summary=", ".join(set(moods)) if moods else None,
                avg_sentiment=sum(sentiments) / len(sentiments) if sentiments else None,
                key_topics=key_topics if key_topics else None,
                last_message_at=datetime.utcnow()
            )
            
            return summary
            
        except Exception as e:
            print(f"Error generating conversation summary: {e}")
            return None
    
    async def delete_old_conversations(
        self,
        user_id: str,
        days_to_keep: int = 90
    ) -> int:
        """Delete conversations older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            result = await self.collection.delete_many({
                "user_id": user_id,
                "created_at": {"$lt": cutoff_date}
            })
            
            return result.deleted_count
        except Exception as e:
            print(f"Error deleting old conversations: {e}")
            return 0
