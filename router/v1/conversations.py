from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.mongodb import get_conversations_collection
from db.mongodb_crud import ConversationCRUD
from db.conversation_crud import ConversationSummaryCRUD, UserMemoryCRUD
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(tags=["conversations"])

@router.get("/conversations/{user_id}")
async def get_user_conversations(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get user's conversations from MongoDB"""
    try:
        conversations_collection = await get_conversations_collection()
        conversation_crud = ConversationCRUD(conversations_collection)
        
        conversations = await conversation_crud.get_user_conversations(
            user_id=user_id,
            limit=limit,
            skip=skip
        )
        
        return {
            "user_id": user_id,
            "conversations": [conv.dict() for conv in conversations],
            "total_returned": len(conversations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversations: {str(e)}")

@router.get("/conversations/{user_id}/recent")
async def get_recent_messages(
    user_id: str,
    limit: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get user's recent messages for context"""
    try:
        conversations_collection = await get_conversations_collection()
        conversation_crud = ConversationCRUD(conversations_collection)
        
        messages = await conversation_crud.get_user_recent_messages(
            user_id=user_id,
            limit=limit
        )
        
        return {
            "user_id": user_id,
            "recent_messages": messages,
            "total_returned": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recent messages: {str(e)}")

@router.get("/conversations/{user_id}/mood-history")
async def get_mood_history(
    user_id: str,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get user's mood history for analysis"""
    try:
        conversations_collection = await get_conversations_collection()
        conversation_crud = ConversationCRUD(conversations_collection)
        
        mood_history = await conversation_crud.get_user_mood_history(
            user_id=user_id,
            days=days
        )
        
        return {
            "user_id": user_id,
            "days_analyzed": days,
            "mood_history": mood_history,
            "total_entries": len(mood_history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving mood history: {str(e)}")

@router.get("/conversations/{user_id}/summaries")
async def get_conversation_summaries(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get user's conversation summaries from PostgreSQL"""
    try:
        summary_crud = ConversationSummaryCRUD()
        
        summaries = await summary_crud.get_user_conversation_summaries(
            db=db,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "user_id": user_id,
            "summaries": [
                {
                    "id": summary.id,
                    "session_id": summary.session_id,
                    "conversation_count": summary.conversation_count,
                    "mood_summary": summary.mood_summary,
                    "avg_sentiment": summary.avg_sentiment,
                    "key_topics": summary.key_topics,
                    "last_message_at": summary.last_message_at,
                    "created_at": summary.created_at
                }
                for summary in summaries
            ],
            "total_returned": len(summaries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation summaries: {str(e)}")

@router.get("/conversations/{user_id}/memory")
async def get_user_memory(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user's memory/summary from PostgreSQL"""
    try:
        memory_crud = UserMemoryCRUD()
        
        memory = await memory_crud.get_user_memory(db=db, user_id=user_id)
        
        if not memory:
            return {
                "user_id": user_id,
                "memory": None,
                "message": "No memory data found for user"
            }
        
        return {
            "user_id": user_id,
            "memory": {
                "current_mood_trend": memory.current_mood_trend,
                "recent_moods": memory.recent_moods,
                "avg_sentiment": memory.avg_sentiment,
                "total_conversations": memory.total_conversations,
                "last_conversation_at": memory.last_conversation_at,
                "progress_summary": memory.progress_summary,
                "created_at": memory.created_at,
                "updated_at": memory.updated_at
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user memory: {str(e)}")

@router.delete("/conversations/{user_id}/cleanup")
async def cleanup_old_conversations(
    user_id: str,
    days_to_keep: int = Query(default=90, ge=30, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Delete old conversations to manage storage"""
    try:
        conversations_collection = await get_conversations_collection()
        conversation_crud = ConversationCRUD(conversations_collection)
        
        deleted_count = await conversation_crud.delete_old_conversations(
            user_id=user_id,
            days_to_keep=days_to_keep
        )
        
        return {
            "user_id": user_id,
            "deleted_conversations": deleted_count,
            "days_kept": days_to_keep,
            "message": f"Successfully deleted {deleted_count} old conversations"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up conversations: {str(e)}")


