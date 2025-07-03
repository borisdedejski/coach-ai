from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import JournalEntry
import json

# Shared model + agent
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
    prompt = f"""
Classify this message into:
- "small_talk" → Greetings or casual chat.
- "off_topic" → Unrelated topics (sports, tech, cars, etc.).
- "mood_entry" → Emotional or mood-related sharing.

Message: "{message}"

Only reply with one of: "small_talk", "off_topic", or "mood_entry".
"""
    response = intent_agent.run(prompt)
    return response.content.strip().lower()

async def detect_intent_with_history(message: str, user_id: str, db: AsyncSession) -> dict:
    """Enhanced intent detection with user history context"""
    history_context = await get_user_history_context(user_id, db)
    
    prompt = f"""
Analyze this message and determine:
1. Intent: "mood_entry", "small_talk", or "off_topic"
2. If mood-related, extract the primary emotion/mood
3. Confidence level (0-1)

User history context: {history_context}

Message: "{message}"

Respond in JSON format:
{{
    "intent": "mood_entry|small_talk|off_topic",
    "primary_mood": "emotion if mood-related, null otherwise",
    "confidence": 0.95,
    "reasoning": "brief explanation"
}}
"""
    
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
    prompt = f"""
You're a friendly psychologist chatbot. Reply casually and kindly to this small talk message:

"{message}"
"""
    response = response_agent.run(prompt)
    return response.content.strip()

def handle_off_topic(message: str) -> str:
    prompt = f"""
You're a psychologist chatbot. Politely explain to the user that you focus only on mental well-being topics, and can't help with this message:

"{message}"
"""
    response = response_agent.run(prompt)
    return response.content.strip()
