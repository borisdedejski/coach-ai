from sqlalchemy import select, desc
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from agents.chat_router_agent import detect_intent_with_history, handle_off_topic, handle_small_talk, handle_mood_entry_with_rag
from agents.reflection_agent import get_reflection_question
from db.session import get_db
from db.models import JournalEntry
from agents.mood_tracker import analyze_mood
from schemas.api_requests import JournalEntryRequest
from schemas.api_responses import ChatResponse
from agents.progress_agent import get_progress_summary
from agents.rag.retriever import RAGRetriever

router = APIRouter(tags=["chat"])

@router.post("/chat", status_code=status.HTTP_200_OK, response_model=ChatResponse)
async def stream_chat(entry: JournalEntryRequest, db: AsyncSession = Depends(get_db)):
    intent_data = await detect_intent_with_history(entry.text, entry.user_id, db)
    intent = intent_data["intent"]

    if intent == "small_talk":
        reply = handle_small_talk(entry.text)
        return ChatResponse(reply=reply, intent=intent)

    elif intent == "off_topic":
        reply = handle_off_topic(entry.text)
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
        reply=rag_response["reply"],
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
