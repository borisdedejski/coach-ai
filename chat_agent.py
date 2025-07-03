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

@cl.on_message
async def main(message: cl.Message):
    """Main chat handler that uses the FastAPI chat endpoint with streaming"""
    
    typing_msg = cl.Message(content="🤔 Processing your message...")
    await typing_msg.send()
    await cl.sleep(0.8)  # Brief pause to show processing
    await typing_msg.remove()
    
    response_data = await send_chat_message(message.content)
    
    # Stream the response
    await stream_response(response_data)

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    await cl.Message(
        content="Hello! I'm your AI Coach. I'm here to help you reflect on your emotions and mental well-being. Share how you're feeling today, and I'll provide personalized insights and reflection questions based on your mood history."
    ).send()

@cl.on_chat_end
async def end():
    """Handle chat session end"""
    await cl.Message(
        content="Thank you for chatting with me today. Remember to take care of yourself and continue reflecting on your emotions. Feel free to come back anytime!"
    ).send()
