from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import JournalEntry
from agents.rag_response_agent import generate_rag_response, generate_mood_specific_response
from agents.prompts.intent import intent_prompt, intent_with_history_prompt
from agents.prompts.small_talk import small_talk_prompt
from agents.prompts.off_topic import off_topic_prompt
import json

model = OpenAIChat(id="gpt-4o-mini")

intent_agent = Agent(
    model=model,
    description="You are an intent classifier for a psychologist chatbot.",
    markdown=False
)

response_agent = Agent(
    model=model,
    description="You are a friendly psychologist chatbot who replies politely and kindly.",
    markdown=False
)

async def get_user_history_context(user_id: str, db: AsyncSession, limit: int = 3) -> str:
    """Get user history context for intent detection"""
    query = select(JournalEntry).where(
        JournalEntry.user_id == user_id
    ).order_by(desc(JournalEntry.timestamp)).limit(limit)
    
    result = await db.execute(query)
    entries = result.scalars().all()
    
    if not entries:
        return "No previous mood history available."
    
    recent_moods = [entry.mood for entry in entries]
    avg_sentiment = sum(entry.sentiment_score for entry in entries) / len(entries)
    
    return f"Recent moods: {', '.join(recent_moods)}, Average sentiment: {avg_sentiment:.2f}"

def detect_intent(message: str) -> str:
    """Legacy intent detection for backward compatibility"""
    prompt = intent_prompt.format(message=message)
    response = intent_agent.run(prompt)
    return response.content.strip().lower()

async def detect_intent_with_history(message: str, user_id: str, db: AsyncSession) -> dict:
    """Enhanced intent detection with user history context"""
    history_context = await get_user_history_context(user_id, db)
    prompt = intent_with_history_prompt.format(history_context=history_context, message=message)
    response = intent_agent.run(prompt)
    try:
        return json.loads(response.content.strip())
    except:
        # Fallback to simple detection
        mood_keywords = ["feel", "mood", "sad", "happy", "angry", "anxious", "depressed", "excited", "worried", "stressed", "upset", "joy", "fear", "love", "hate"]
        is_mood_related = any(word in message.lower() for word in mood_keywords)
        return {
            "intent": "mood_entry" if is_mood_related else "small_talk",
            "primary_mood": None,
            "confidence": 0.7,
            "reasoning": "fallback keyword detection"
        }

def handle_small_talk(message: str) -> str:
    """Handle small talk with RAG enhancement"""
    rag_result = generate_rag_response(
        user_message=message,
        user_context="User is engaging in casual conversation",
        use_knowledge_base=True
    )
    if rag_result["used_knowledge_base"] and rag_result["similarity_score"] > 0.4:
        return rag_result["response"]
    prompt = small_talk_prompt.format(message=message)
    response = response_agent.run(prompt)
    return response.content.strip()

def handle_off_topic(message: str) -> str:
    prompt = off_topic_prompt.format(message=message)
    response = response_agent.run(prompt)
    return response.content.strip()

async def handle_mood_entry_with_rag(message: str, user_id: str, db: AsyncSession, mood: str, sentiment_score: float) -> dict:
    """Handle mood entries with RAG-enhanced responses"""
    history_context = await get_user_history_context(user_id, db)
    
    rag_result = generate_mood_specific_response(
        user_message=message,
        mood=mood,
        sentiment_score=sentiment_score,
        user_context=history_context
    )
    
    return {
        "reply": rag_result["response"],
        "knowledge_context": rag_result["knowledge_context"],
        "similarity_score": rag_result["similarity_score"],
        "used_knowledge_base": rag_result["used_knowledge_base"]
    }
