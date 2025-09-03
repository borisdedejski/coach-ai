import chainlit as cl
import requests
import json
from typing import Dict, Any, List
from datetime import datetime

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

async def get_daily_checkin(user_id: str = USER_ID) -> Dict[str, Any]:
    """Get personalized daily check-in prompt"""
    try:
        response = requests.get(
            f"{BASE_URL}/habits/daily-checkin?user_id={user_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error fetching daily checkin: {e}")
        return None

async def get_user_habits(user_id: str = USER_ID) -> List[Dict[str, Any]]:
    """Get user's active habits"""
    try:
        response = requests.get(
            f"{BASE_URL}/habits/my-habits?user_id={user_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print(f"Error fetching user habits: {e}")
        return []

async def get_available_habits() -> List[Dict[str, Any]]:
    """Get all available habits"""
    try:
        response = requests.get(
            f"{BASE_URL}/habits/available",
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print(f"Error fetching available habits: {e}")
        return []

async def add_user_habit(user_id: str, habit_id: int, target_value: float = None, reminder_time: str = None) -> bool:
    """Add a habit for a user"""
    try:
        params = {"user_id": user_id, "habit_id": habit_id}
        if target_value is not None:
            params["target_value"] = target_value
        if reminder_time is not None:
            params["reminder_time"] = reminder_time
            
        response = requests.post(
            f"{BASE_URL}/habits/add-habit",
            params=params,
            timeout=30
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error adding habit: {e}")
        return False

async def log_activity(user_id: str, habit_id: int, value: float = None, completed: bool = True, notes: str = None) -> bool:
    """Log a user's activity"""
    try:
        params = {
            "user_id": user_id,
            "habit_id": habit_id,
            "completed": completed
        }
        if value is not None:
            params["value"] = value
        if notes is not None:
            params["notes"] = notes
            
        response = requests.post(
            f"{BASE_URL}/habits/log-activity",
            params=params,
            timeout=30
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error logging activity: {e}")
        return False

async def get_habit_progress(user_id: str = USER_ID, days: int = 7) -> Dict[str, Any]:
    """Get user's habit progress"""
    try:
        response = requests.get(
            f"{BASE_URL}/habits/progress?user_id={user_id}&days={days}",
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error fetching habit progress: {e}")
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

async def display_habit_progress(progress_data: Dict[str, Any]):
    """Display habit progress and streaks"""
    if not progress_data or not progress_data.get("progress"):
        return
    
    progress = progress_data["progress"]
    
    if not progress:
        await cl.Message(content="📝 **Habit Progress:** No habits tracked yet. Use '/habits' to set up your first habit!").send()
        return
    
    progress_msg = "## 💪 **Habit Progress & Streaks**\n\n"
    
    for habit_name, data in progress.items():
        completion_rate = data.get("completion_rate", 0)
        current_streak = data.get("current_streak", 0)
        longest_streak = data.get("longest_streak", 0)
        target_value = data.get("target_value")
        unit = data.get("unit", "")
        
        # Progress bar emoji
        if completion_rate >= 80:
            progress_bar = "🟢"
        elif completion_rate >= 50:
            progress_bar = "🟡"
        else:
            progress_bar = "🔴"
        
        progress_msg += f"**{habit_name}** {progress_bar}\n"
        progress_msg += f"• Completion: {completion_rate}% ({data.get('completed_days', 0)}/{data.get('total_days', 0)} days)\n"
        progress_msg += f"• Current Streak: {current_streak} days\n"
        progress_msg += f"• Longest Streak: {longest_streak} days\n"
        if target_value:
            progress_msg += f"• Target: {target_value} {unit}\n"
        progress_msg += "\n"
    
    await cl.Message(content=progress_msg).send()

async def show_habit_setup():
    """Show habit setup interface"""
    habits = await get_available_habits()
    
    if not habits:
        await cl.Message(content="❌ No habits available. Please check the server.").send()
        return
    
    # Group habits by category
    categories = {}
    for habit in habits:
        category = habit.get("category", "Other")
        if category not in categories:
            categories[category] = []
        categories[category].append(habit)
    
    setup_msg = "## 🎯 **Available Habits to Track**\n\n"
    setup_msg += "Choose habits that resonate with you. You can add multiple habits and track your progress!\n\n"
    
    for category, category_habits in categories.items():
        setup_msg += f"### {category.title()}\n"
        for habit in category_habits:
            setup_msg += f"• **{habit['name']}** - {habit['description']}\n"
            setup_msg += f"  Target: {habit.get('target_value', 'N/A')} {habit.get('unit', '')}\n"
            setup_msg += f"  Benefit: {habit['mental_health_benefit']}\n\n"
    
    setup_msg += "**To add a habit:** Type 'add habit [habit name]' or 'setup habits'\n"
    setup_msg += "**To log activity:** Type 'log [habit name] [value]' or 'complete [habit name]'\n"
    setup_msg += "**To see progress:** Type '/habits' or 'show habits'\n"
    
    await cl.Message(content=setup_msg).send()

@cl.action_callback("show_progress")
async def on_show_progress(action):
    """Handle the show progress action"""
    await cl.Message(content="📊 Analyzing your progress patterns...").send()
    
    progress_data = await get_enhanced_progress()
    if progress_data:
        await display_enhanced_progress(progress_data)
    else:
        await cl.Message(content="❌ Unable to fetch progress data. Please try again later.").send()

@cl.action_callback("show_habits")
async def on_show_habits(action):
    """Handle the show habits action"""
    await cl.Message(content="💪 Loading your habit progress...").send()
    
    progress_data = await get_habit_progress()
    if progress_data:
        await display_habit_progress(progress_data)
    else:
        await cl.Message(content="❌ Unable to fetch habit data. Please try again later.").send()

@cl.on_message
async def main(message: cl.Message):
    """Main chat handler with habit tracking integration"""
    
    # Handle commands
    content = message.content.lower().strip()
    
    if content.startswith("/progress") or content.startswith("show progress"):
        await on_show_progress(None)
        return
    
    if content.startswith("/habits") or content.startswith("show habits"):
        await on_show_habits(None)
        return
    
    if content.startswith("setup habits") or content.startswith("add habits"):
        await show_habit_setup()
        return
    
    if content.startswith("add habit "):
        # Parse habit addition
        habit_name = content[10:].strip()
        await cl.Message(content=f"🎯 Adding habit: {habit_name}\n\nI'll help you set this up. What's your target for {habit_name}?").send()
        return
    
    if content.startswith("log ") or content.startswith("complete "):
        # Parse activity logging
        parts = content.split(" ", 2)
        if len(parts) >= 2:
            habit_name = parts[1]
            value = parts[2] if len(parts) > 2 else None
            await cl.Message(content=f"📝 Logging activity for {habit_name}...\n\nI'll help you log this. What value did you achieve?").send()
        return
    
    # Regular chat processing
    typing_msg = cl.Message(content="🤔 Processing your message...")
    await typing_msg.send()
    await cl.sleep(0.8)
    await typing_msg.remove()
    
    response_data = await send_chat_message(message.content)
    
    # Stream the response
    await stream_response(response_data)
    
    # If this was a mood-related entry, show enhanced progress analysis
    if response_data.get("mood") and response_data.get("intent") != "error":
        await cl.sleep(1.0)
        
        # Get enhanced progress data
        progress_data = await get_enhanced_progress()
        if progress_data:
            await display_enhanced_progress(progress_data)

@cl.on_chat_start
async def start():
    """Initialize the chat session with proactive features"""
    # Check if this is a new day and show daily check-in
    checkin_data = await get_daily_checkin()
    
    if checkin_data and checkin_data.get("prompt"):
        await cl.Message(content=checkin_data["prompt"]).send()
    else:
        await cl.Message(
            content="Hello! I'm your AI Coach. I'm here to help you reflect on your emotions and mental well-being. Share how you're feeling today, and I'll provide personalized insights and reflection questions based on your mood history.\n\n💡 **Available Commands:**\n• `/progress` - See detailed mood analysis\n• `/habits` - View habit progress and streaks\n• `setup habits` - Add new habits to track\n• `add habit [name]` - Add a specific habit\n• `log [habit] [value]` - Log activity completion"
        ).send()
    
    # Show habit progress if user has habits
    progress_data = await get_habit_progress()
    if progress_data and progress_data.get("progress"):
        await cl.sleep(1.0)
        await display_habit_progress(progress_data)

@cl.on_chat_end
async def end():
    """Handle chat session end"""
    await cl.Message(
        content="👋 Thank you for chatting with me today! Remember to log your habits and check in tomorrow. Take care! 🌟"
    ).send()
