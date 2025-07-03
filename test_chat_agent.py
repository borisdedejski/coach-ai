#!/usr/bin/env python3
"""
Test script for the chat agent that uses the FastAPI endpoint
"""
import asyncio
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/v1"
USER_ID = "test_user"

async def test_chat_agent():
    """Test the chat agent functionality"""
    
    # Test messages
    test_messages = [
        "I'm feeling really anxious today about my presentation",
        "Hello, how are you?",
        "What's the weather like?",
        "I've been feeling much better since we last talked",
        "I'm so excited about my new job!"
    ]
    
    print("=== Testing Chat Agent with FastAPI Endpoint ===\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: '{message}'")
        print("-" * 50)
        
        try:
            # Send message to chat API
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"text": message, "user_id": USER_ID},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"Reply: {data.get('reply', 'No reply')}")
                print(f"Intent: {data.get('intent', 'Unknown')}")
                
                if data.get('mood'):
                    print(f"Mood: {data['mood']} (score: {data['sentiment_score']:.2f})")
                
                if data.get('reflection_question'):
                    print(f"Reflection: {data['reflection_question'][:80]}...")
                
                if data.get('progress_summary'):
                    print(f"Progress: {data['progress_summary'][:80]}...")
                
            else:
                print(f"❌ Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the FastAPI server is running on localhost:8000")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print()

def test_server_status():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL.replace('/v1', '')}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the FastAPI server first:")
        print("   python main.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server status: {e}")
        return False

if __name__ == "__main__":
    # Check server status first
    if test_server_status():
        print("\n" + "="*60 + "\n")
        asyncio.run(test_chat_agent())
    else:
        print("\nPlease start the server first and try again.") 