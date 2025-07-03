#!/usr/bin/env python3
"""
Helper script to run the complete chat system with ChromaDB RAG
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

def setup_chroma():
    """Set up ChromaDB vector store if not already set up"""
    print("🔍 Checking ChromaDB vector store...")
    
    chroma_db_path = Path("knowledge/embeddings/chroma_db")
    embeddings_path = Path("knowledge/embeddings/mental_health_embeddings.npy")
    
    if chroma_db_path.exists() and any(chroma_db_path.iterdir()):
        print("✅ ChromaDB already exists")
        return True
    
    if not embeddings_path.exists():
        print("⚠️  Knowledge base not indexed. Running index_knowledge_base.py...")
        try:
            result = subprocess.run([sys.executable, "scripts/index_knowledge_base.py"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                print(f"❌ Failed to index knowledge base: {result.stderr}")
                return False
            print("✅ Knowledge base indexed successfully")
        except Exception as e:
            print(f"❌ Error indexing knowledge base: {e}")
            return False
    
    print("🔧 Setting up ChromaDB vector store...")
    try:
        result = subprocess.run([sys.executable, "scripts/setup_chroma.py"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"❌ Failed to setup ChromaDB: {result.stderr}")
            return False
        print("✅ ChromaDB vector store setup complete")
        return True
    except Exception as e:
        print(f"❌ Error setting up ChromaDB: {e}")
        return False

def test_rag_system():
    """Test RAG system functionality"""
    print("🧪 Testing RAG system...")
    try:
        result = subprocess.run([sys.executable, "test_chroma_demo.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ RAG system test passed")
            return True
        else:
            print(f"⚠️  RAG system test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️  Could not test RAG system: {e}")
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
        # Set environment variable to disable Chainlit database
        env = os.environ.copy()
        env['CHAINLIT_DISABLE_DATABASE'] = 'true'
        
        subprocess.run([sys.executable, "-m", "chainlit", "run", "chat_agent.py", "--port", "8001"], 
                      env=env)
    except KeyboardInterrupt:
        print("\n👋 Chat session ended")
    except Exception as e:
        print(f"❌ Error starting Chainlit: {e}")

def main():
    """Main function to run the complete system"""
    print("🤖 AI Coach Chat System with ChromaDB RAG")
    print("=" * 50)
    
    # Set up ChromaDB vector store
    if not setup_chroma():
        print("⚠️  ChromaDB setup failed, but continuing with system startup...")
    
    # Test RAG system (optional)
    test_rag_system()
    
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