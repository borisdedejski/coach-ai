#!/usr/bin/env python3
"""
Helper script to run the complete chat system
"""
import subprocess
import time
import sys
import os
import requests
from pathlib import Path

def check_server_running():
    """Check if the FastAPI server is running"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    try:
        # Start server in background
        server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_server_running():
                print("✅ Server is running on http://localhost:8000")
                return server_process
            time.sleep(1)
            print(f"   Checking... ({i+1}/30)")
        
        print("❌ Server failed to start within 30 seconds")
        server_process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def start_chainlit():
    """Start the Chainlit chat interface"""
    print("\n🎨 Starting Chainlit chat interface...")
    try:
        subprocess.run([sys.executable, "-m", "chainlit", "run", "chat_agent.py", "--port", "8001"])
    except KeyboardInterrupt:
        print("\n👋 Chat session ended")
    except Exception as e:
        print(f"❌ Error starting Chainlit: {e}")

def main():
    """Main function to run the complete system"""
    print("🤖 AI Coach Chat System")
    print("=" * 40)
    
    # Check if server is already running
    if check_server_running():
        print("✅ Server is already running")
    else:
        # Start server
        server_process = start_server()
        if not server_process:
            print("❌ Failed to start server. Exiting.")
            sys.exit(1)
    
    # Start Chainlit
    try:
        start_chainlit()
    finally:
        # Cleanup
        if 'server_process' in locals() and server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()

if __name__ == "__main__":
    main() 