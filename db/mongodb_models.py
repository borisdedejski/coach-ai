from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class ConversationMessage(BaseModel):
    """Individual message in a conversation"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ConversationDocument(BaseModel):
    """MongoDB document for storing conversations"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    messages: List[ConversationMessage] = Field(..., description="List of messages in the conversation")
    
    # Analysis data
    mood: Optional[str] = Field(None, description="Detected mood")
    sentiment_score: Optional[float] = Field(None, description="Sentiment analysis score")
    intent: Optional[str] = Field(None, description="Detected intent")
    
    # AI-generated content
    reflection_question: Optional[str] = Field(None, description="Generated reflection question")
    progress_summary: Optional[str] = Field(None, description="Progress summary")
    progress_score: Optional[float] = Field(None, description="Progress score")
    
    # RAG metadata
    used_knowledge_base: Optional[bool] = Field(None, description="Whether knowledge base was used")
    similarity_score: Optional[float] = Field(None, description="Similarity score for RAG")
    knowledge_context: Optional[str] = Field(None, description="Context from knowledge base")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ConversationSummary(BaseModel):
    """Summary of a conversation for PostgreSQL storage"""
    user_id: str
    session_id: str
    conversation_count: int = Field(..., description="Number of messages in conversation")
    mood_summary: Optional[str] = Field(None, description="Summary of moods in conversation")
    avg_sentiment: Optional[float] = Field(None, description="Average sentiment score")
    key_topics: Optional[List[str]] = Field(None, description="Key topics discussed")
    last_message_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserMemory(BaseModel):
    """User memory/summary for PostgreSQL storage"""
    user_id: str
    current_mood_trend: Optional[str] = Field(None, description="Current mood trend")
    recent_moods: Optional[List[str]] = Field(None, description="Recent mood history")
    avg_sentiment: Optional[float] = Field(None, description="Average sentiment over time")
    total_conversations: int = Field(default=0, description="Total number of conversations")
    last_conversation_at: Optional[datetime] = Field(None, description="Last conversation timestamp")
    progress_summary: Optional[str] = Field(None, description="Overall progress summary")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
