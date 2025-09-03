from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import ConversationSummary, UserMemory, JournalEntry
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

class ConversationSummaryCRUD:
    """CRUD operations for conversation summaries in PostgreSQL"""
    
    async def create_conversation_summary(
        self,
        db: AsyncSession,
        user_id: str,
        session_id: str,
        conversation_count: int,
        mood_summary: Optional[str] = None,
        avg_sentiment: Optional[float] = None,
        key_topics: Optional[List[str]] = None
    ) -> ConversationSummary:
        """Create a new conversation summary"""
        
        summary = ConversationSummary(
            user_id=user_id,
            session_id=session_id,
            conversation_count=conversation_count,
            mood_summary=mood_summary,
            avg_sentiment=avg_sentiment,
            key_topics=key_topics,
            last_message_at=datetime.utcnow()
        )
        
        db.add(summary)
        await db.commit()
        await db.refresh(summary)
        return summary
    
    async def get_user_conversation_summaries(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 10
    ) -> List[ConversationSummary]:
        """Get user's conversation summaries"""
        result = await db.execute(
            select(ConversationSummary)
            .where(ConversationSummary.user_id == user_id)
            .order_by(ConversationSummary.last_message_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent_summaries_for_analysis(
        self,
        db: AsyncSession,
        user_id: str,
        days: int = 30
    ) -> List[ConversationSummary]:
        """Get recent summaries for mood analysis"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(ConversationSummary)
            .where(
                ConversationSummary.user_id == user_id,
                ConversationSummary.last_message_at >= start_date
            )
            .order_by(ConversationSummary.last_message_at.desc())
        )
        return result.scalars().all()

class UserMemoryCRUD:
    """CRUD operations for user memory in PostgreSQL"""
    
    async def get_user_memory(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Optional[UserMemory]:
        """Get user's memory/summary"""
        result = await db.execute(
            select(UserMemory).where(UserMemory.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_or_update_user_memory(
        self,
        db: AsyncSession,
        user_id: str,
        current_mood_trend: Optional[str] = None,
        recent_moods: Optional[List[str]] = None,
        avg_sentiment: Optional[float] = None,
        total_conversations: Optional[int] = None,
        progress_summary: Optional[str] = None
    ) -> UserMemory:
        """Create or update user memory"""
        
        # Check if user memory exists
        existing_memory = await self.get_user_memory(db, user_id)
        
        if existing_memory:
            # Update existing memory
            update_data = {
                "updated_at": datetime.utcnow(),
                "last_conversation_at": datetime.utcnow()
            }
            
            if current_mood_trend is not None:
                update_data["current_mood_trend"] = current_mood_trend
            if recent_moods is not None:
                update_data["recent_moods"] = recent_moods
            if avg_sentiment is not None:
                update_data["avg_sentiment"] = avg_sentiment
            if total_conversations is not None:
                update_data["total_conversations"] = total_conversations
            if progress_summary is not None:
                update_data["progress_summary"] = progress_summary
            
            await db.execute(
                update(UserMemory)
                .where(UserMemory.user_id == user_id)
                .values(**update_data)
            )
            await db.commit()
            await db.refresh(existing_memory)
            return existing_memory
        else:
            # Create new memory
            memory = UserMemory(
                user_id=user_id,
                current_mood_trend=current_mood_trend,
                recent_moods=recent_moods,
                avg_sentiment=avg_sentiment,
                total_conversations=total_conversations or 0,
                progress_summary=progress_summary,
                last_conversation_at=datetime.utcnow()
            )
            
            db.add(memory)
            await db.commit()
            await db.refresh(memory)
            return memory
    
    async def update_user_mood_trend(
        self,
        db: AsyncSession,
        user_id: str,
        mood_trend: str,
        recent_moods: List[str],
        avg_sentiment: float
    ) -> bool:
        """Update user's mood trend and recent moods"""
        try:
            await db.execute(
                update(UserMemory)
                .where(UserMemory.user_id == user_id)
                .values(
                    current_mood_trend=mood_trend,
                    recent_moods=recent_moods,
                    avg_sentiment=avg_sentiment,
                    updated_at=datetime.utcnow()
                )
            )
            await db.commit()
            return True
        except Exception as e:
            print(f"Error updating user mood trend: {e}")
            return False

# Legacy support for existing JournalEntry operations
class LegacyJournalCRUD:
    """Legacy CRUD operations for backward compatibility"""
    
    async def get_last_journal_entries(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 3
    ) -> List[JournalEntry]:
        """Get last journal entries for backward compatibility"""
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_user_entries_for_analysis(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 20
    ) -> List[JournalEntry]:
        """Get user entries for analysis (legacy)"""
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()


