import chainlit as cl
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/v1"
USER_ID = "default_user"  # You can make this dynamic based on user session

async def send_chat_message(text: str, user_id: str = USER_ID) -> Dict[str, Any]:
    """Send a message to the chat API and get response"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"text": text, "user_id": user_id},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "reply": f"Sorry, I encountered an error (Status: {response.status_code})",
                "intent": "error",
                "mood": None,
                "sentiment_score": 0.0,
                "reflection_question": None,
                "progress_summary": None,
                "progress_score": None
            }
    except requests.exceptions.ConnectionError:
        return {
            "reply": "Sorry, I can't connect to the chat service. Please make sure the server is running.",
            "intent": "error",
            "mood": None,
            "sentiment_score": 0.0,
            "reflection_question": None,
            "progress_summary": None,
            "progress_score": None
        }
    except Exception as e:
        return {
            "reply": f"Sorry, an unexpected error occurred: {str(e)}",
            "intent": "error",
            "mood": None,
            "sentiment_score": 0.0,
            "reflection_question": None,
            "progress_summary": None,
            "progress_score": None
        }

async def get_enhanced_progress(user_id: str = USER_ID) -> Dict[str, Any]:
    """Get enhanced progress analysis with patterns and trends"""
    try:
        response = requests.get(
            f"{BASE_URL}/progress/{user_id}/enhanced",
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error fetching enhanced progress: {e}")
        return None

async def stream_response(response_data: Dict[str, Any]):
    """Stream the response in a natural way"""
    reply = response_data.get("reply", "No response received")
    
    # Create a streaming message
    msg = cl.Message(content="")
    await msg.send()
    
    for char in reply:
        await msg.stream_token(char)
        # Vary the delay slightly to make it feel more human
        await cl.sleep(0.02 + (0.01 if char in '.!?' else 0))
    
    if response_data.get("mood"):
        await cl.sleep(0.5)  # Pause before additional info
        await msg.stream_token(f"\n\n**Mood Detected:** {response_data['mood']} (Score: {response_data['sentiment_score']:.2f})")
    
    if response_data.get("reflection_question"):
        await cl.sleep(0.3)
        await msg.stream_token(f"\n\n**Reflection Question:** {response_data['reflection_question']}")
    
    if response_data.get("progress_summary"):
        await cl.sleep(0.3)
        await msg.stream_token(f"\n\n**Progress Summary:** {response_data['progress_summary']}")
    
    if response_data.get("progress_score") is not None:
        await cl.sleep(0.2)
        await msg.stream_token(f"\n**Progress Score:** {response_data['progress_score']:.2f}")
    
    await msg.update()

async def display_enhanced_progress(progress_data: Dict[str, Any]):
    """Display enhanced progress analysis with patterns and trends"""
    if not progress_data or not progress_data.get("patterns"):
        return
    
    patterns = progress_data["patterns"]
    
    # Create a detailed progress message
    progress_msg = "## 📊 **Enhanced Progress Analysis**\n\n"
    
    # Mood Direction
    mood_direction = patterns.get("mood_direction", {})
    if mood_direction.get("direction") != "insufficient_data":
        direction = mood_direction.get("direction", "stable")
        stability = mood_direction.get("stability", "unknown")
        progress_msg += f"**Overall Mood Direction:** {direction.replace('_', ' ').title()}\n"
        progress_msg += f"**Mood Stability:** {stability.replace('_', ' ').title()}\n\n"
    
    # Day of Week Patterns
    day_patterns = patterns.get("day_patterns", {})
    if day_patterns:
        progress_msg += "**📅 Day-of-Week Patterns:**\n"
        for day, data in day_patterns.items():
            avg_sentiment = data.get("avg_sentiment", 0)
            common_mood = data.get("most_common_mood", "unknown")
            entry_count = data.get("entry_count", 0)
            progress_msg += f"• **{day}:** {common_mood} (avg score: {avg_sentiment:.2f}, {entry_count} entries)\n"
        progress_msg += "\n"
    
    # Trend Analysis
    trend_analysis = patterns.get("trend_analysis", {})
    if trend_analysis.get("trend") == "analyzed":
        direction = trend_analysis.get("direction", "stable")
        change_mag = trend_analysis.get("change_magnitude", 0)
        progress_msg += f"**📈 Recent Trend:** {direction.title()} (change: {change_mag:.2f})\n\n"
    
    # Trigger Analysis
    trigger_analysis = patterns.get("trigger_analysis", {})
    most_frequent = trigger_analysis.get("most_frequent", [])
    if most_frequent:
        progress_msg += "**🎯 Frequent Themes:**\n"
        for trigger in most_frequent:
            trigger_name = trigger.replace("_", " ").title()
            progress_msg += f"• {trigger_name}\n"
        progress_msg += "\n"
    
    # Progress Score
    if progress_data.get("score") is not None:
        progress_msg += f"**📊 Progress Score:** {progress_data['score']:.2f}/1.0\n"
    
    await cl.Message(content=progress_msg).send()

@cl.action_callback("show_progress")
async def on_show_progress(action):
    """Handle the show progress action"""
    await cl.Message(content="📊 Analyzing your progress patterns...").send()
    
    progress_data = await get_enhanced_progress()
    if progress_data:
        await display_enhanced_progress(progress_data)
    else:
        await cl.Message(content="❌ Unable to fetch progress data. Please try again later.").send()

@cl.on_message
async def main(message: cl.Message):
    """Main chat handler that uses the FastAPI chat endpoint with streaming"""
    
    # Check if this is a command
    if message.content.lower().startswith("/progress") or message.content.lower().startswith("show progress"):
        await on_show_progress(None)
        return
    
    typing_msg = cl.Message(content="🤔 Processing your message...")
    await typing_msg.send()
    await cl.sleep(0.8)  # Brief pause to show processing
    await typing_msg.remove()
    
    response_data = await send_chat_message(message.content)
    
    # Stream the response
    await stream_response(response_data)
    
    # If this was a mood-related entry, show enhanced progress analysis
    if response_data.get("mood") and response_data.get("intent") != "error":
        await cl.sleep(1.0)  # Pause before showing progress analysis
        
        # Get enhanced progress data
        progress_data = await get_enhanced_progress()
        if progress_data:
            await display_enhanced_progress(progress_data)

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    await cl.Message(
        content="Hello! I'm your AI Coach. I'm here to help you reflect on your emotions and mental well-being. Share how you're feeling today, and I'll provide personalized insights and reflection questions based on your mood history.\n\n💡 **Tip:** Type '/progress' or 'show progress' to see detailed analysis of your mood patterns and trends."
    ).send()

@cl.on_chat_end
async def end():
    """Handle chat session end"""
    await cl.Message(
        content="Thank you for chatting with me today. Remember to take care of yourself and continue reflecting on your emotions. Feel free to come back anytime!"
    ).send()
