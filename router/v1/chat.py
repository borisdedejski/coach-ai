from sqlalchemy import select, desc
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from agents.chat_router_agent import detect_intent_with_history, handle_off_topic, handle_small_talk, handle_mood_entry_with_rag
from agents.reflection_agent import get_reflection_question
from db.session import get_db
from db.models import JournalEntry
from db.mongodb import get_conversations_collection
from db.mongodb_crud import ConversationCRUD
from db.conversation_crud import ConversationSummaryCRUD, UserMemoryCRUD
from agents.mood_tracker import analyze_mood
from schemas.api_requests import JournalEntryRequest
from schemas.api_responses import ChatResponse
from agents.progress_agent import get_progress_summary
from agents.rag.retriever import RAGRetriever
from service.habit_service import HabitService
import uuid
from datetime import datetime

router = APIRouter(tags=["chat"])

habit_service = HabitService()

async def enhance_response_with_habits(reply: str, user_id: str, db: AsyncSession) -> str:
    """Enhance the response with habit-related suggestions and context"""
    try:
        # Get user's habit progress
        progress = await habit_service.get_user_progress(db, user_id, days=7)
        
        if not progress:
            # No habits yet - suggest setting up habits
            return reply + "\n\n💡 **Proactive Tip:** Would you like to set up some healthy habits to track? Type 'setup habits' to see available options that can support your mental well-being."
        
        # Check for low completion habits
        low_completion_habits = [
            name for name, data in progress.items() 
            if data["completion_rate"] < 50
        ]
        
        # Check for good streaks
        good_streaks = [
            name for name, data in progress.items() 
            if data["current_streak"] >= 3
        ]
        
        enhanced_reply = reply
        
        # Add celebration for good streaks
        if good_streaks:
            enhanced_reply += f"\n\n🎉 **Great job!** You're maintaining a {', '.join(good_streaks)} streak! Keep up the excellent work!"
        
        # Add gentle encouragement for low completion habits
        if low_completion_habits:
            enhanced_reply += f"\n\n💪 **Gentle Reminder:** Consider working on {', '.join(low_completion_habits[:2])} today. Small steps lead to big changes!"
        
        # Add habit logging suggestion
        enhanced_reply += "\n\n📝 **Quick Log:** You can log your activities with 'log [habit name] [value]' or see your progress with '/habits'"
        
        return enhanced_reply
        
    except Exception as e:
        print(f"Error enhancing response with habits: {e}")
        return reply

@router.post("/chat", status_code=status.HTTP_200_OK, response_model=ChatResponse)
async def stream_chat(entry: JournalEntryRequest, db: AsyncSession = Depends(get_db)):
    # Get MongoDB collection
    conversations_collection = await get_conversations_collection()
    conversation_crud = ConversationCRUD(conversations_collection)
    summary_crud = ConversationSummaryCRUD()
    memory_crud = UserMemoryCRUD()
    
    # Generate session ID for this conversation
    session_id = str(uuid.uuid4())
    
    intent_data = await detect_intent_with_history(entry.text, entry.user_id, db)
    intent = intent_data["intent"]

    if intent == "small_talk":
        reply = handle_small_talk(entry.text)
        # Enhance small talk with habit context
        enhanced_reply = await enhance_response_with_habits(reply, entry.user_id, db)
        
        # Store conversation in MongoDB
        await conversation_crud.create_conversation(
            user_id=entry.user_id,
            session_id=session_id,
            user_message=entry.text,
            assistant_reply=enhanced_reply,
            intent=intent
        )
        
        return ChatResponse(reply=enhanced_reply, intent=intent)

    elif intent == "off_topic":
        reply = handle_off_topic(entry.text)
        
        # Store conversation in MongoDB
        await conversation_crud.create_conversation(
            user_id=entry.user_id,
            session_id=session_id,
            user_message=entry.text,
            assistant_reply=reply,
            intent=intent
        )
        
        return ChatResponse(reply=reply, intent=intent)

    result = analyze_mood(entry.text)
    
    rag_response = await handle_mood_entry_with_rag(
        message=entry.text,
        user_id=entry.user_id,
        db=db,
        mood=result["mood"],
        sentiment_score=result["sentiment_score"]
    )
    
    reflection_question = await get_reflection_question(db, entry.user_id, result["mood"])
    progress_data = await get_progress_summary(db, entry.user_id)
    summary = progress_data.get("summary")
    score = progress_data.get("score")

    # Enhance the response with habit context
    enhanced_reply = await enhance_response_with_habits(rag_response["reply"], entry.user_id, db)

    # Store full conversation in MongoDB
    conversation_id = await conversation_crud.create_conversation(
        user_id=entry.user_id,
        session_id=session_id,
        user_message=entry.text,
        assistant_reply=enhanced_reply,
        mood=result["mood"],
        sentiment_score=result["sentiment_score"],
        intent=intent,
        reflection_question=reflection_question,
        progress_summary=summary,
        progress_score=score,
        used_knowledge_base=rag_response["used_knowledge_base"],
        similarity_score=rag_response["similarity_score"],
        knowledge_context=rag_response["knowledge_context"]
    )
    
    # Create conversation summary for PostgreSQL
    await summary_crud.create_conversation_summary(
        db=db,
        user_id=entry.user_id,
        session_id=session_id,
        conversation_count=2,  # user message + assistant reply
        mood_summary=result["mood"],
        avg_sentiment=result["sentiment_score"],
        key_topics=[result["mood"]] if result["mood"] else None
    )
    
    # Update user memory
    await memory_crud.create_or_update_user_memory(
        db=db,
        user_id=entry.user_id,
        current_mood_trend=result["mood"],
        recent_moods=[result["mood"]] if result["mood"] else None,
        avg_sentiment=result["sentiment_score"],
        progress_summary=summary
    )

    # Keep legacy JournalEntry for backward compatibility during migration
    journal_entry = JournalEntry(
        user_id=entry.user_id,
        text=entry.text,
        mood=result["mood"],
        sentiment_score=result["sentiment_score"],
        reflection_question=reflection_question,
        progress_summary=summary,
        progress_score=score,
    )

    db.add(journal_entry)
    await db.commit()
    await db.refresh(journal_entry)

    return ChatResponse(
        reply=enhanced_reply,
        intent=intent,
        mood=result["mood"],
        sentiment_score=result["sentiment_score"],
        reflection_question=reflection_question,
        progress_summary=summary,
        progress_score=score,
        # RAG metadata
        used_knowledge_base=rag_response["used_knowledge_base"],
        similarity_score=rag_response["similarity_score"],
        knowledge_context=rag_response["knowledge_context"]
    )
