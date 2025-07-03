# AI Coach Chat System

This system provides a conversational AI coach that helps users reflect on their emotions and mental well-being. It combines a FastAPI backend with a Chainlit frontend for an interactive chat experience.

## 🏗️ Architecture

- **FastAPI Backend** (`main.py`): Handles chat logic, mood analysis, and database operations
- **Chainlit Frontend** (`chat_agent.py`): Provides the chat interface
- **Database**: Stores conversation history and mood data
- **AI Agents**: Handle intent detection, mood analysis, and response generation

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
python run_chat_system.py
```
This will automatically start both the server and chat interface.

### Option 2: Manual Setup

1. **Start the FastAPI server:**
   ```bash
   python main.py
   ```
   The server will run on `http://localhost:8000`

2. **Start the Chainlit chat interface:**
   ```bash
   chainlit run chat_agent.py --port 8001
   ```
   The chat interface will be available at `http://localhost:8001`

## 🧪 Testing

Test the system with:
```bash
python test_chat_agent.py
```

This will test various message types and verify the system is working correctly.

## 🔧 Configuration

### Environment Variables
Make sure you have a `.env` file with:
```
DATABASE_URL=your_database_connection_string
OPENAI_API_KEY=your_openai_api_key
```

### User ID
The system uses a default user ID (`default_user`). You can modify this in `chat_agent.py` to support multiple users.

## 📊 Features

### Chat Capabilities
- **Mood Detection**: Automatically detects and analyzes user emotions
- **Intent Classification**: Distinguishes between mood entries, small talk, and off-topic conversations
- **Contextual Responses**: Uses conversation history to provide personalized responses
- **Progress Tracking**: Monitors emotional progress over time
- **Reflection Questions**: Generates thoughtful questions to encourage self-reflection

### Response Types
1. **Mood Entries**: Full analysis with mood detection, reflection questions, and progress tracking
2. **Small Talk**: Friendly, casual responses
3. **Off-Topic**: Polite redirection to mental well-being topics

## 🔄 How It Works

1. **User sends message** → Chainlit interface
2. **Message forwarded** → FastAPI `/v1/chat` endpoint
3. **Intent detection** → Determines if mood-related, small talk, or off-topic
4. **Mood analysis** → Analyzes emotional content (if mood-related)
5. **Context retrieval** → Gets user's conversation history
6. **Response generation** → Creates personalized response with reflection questions
7. **Database storage** → Saves mood entries for future context
8. **Response formatting** → Formats response for display in chat interface

## 🛠️ Troubleshooting

### Connection Issues
- Ensure the FastAPI server is running on port 8000
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify your `.env` file has the correct database URL

### Database Issues
- Run database migrations: `alembic upgrade head`
- Check your database connection string in `.env`

### AI Model Issues
- Verify your OpenAI API key is set correctly
- Check that you have sufficient API credits

## 📁 File Structure

```
coach-ai/
├── main.py                 # FastAPI server
├── chat_agent.py          # Chainlit chat interface
├── run_chat_system.py     # Automated startup script
├── test_chat_agent.py     # Testing script
├── router/v1/chat.py      # Chat API endpoints
├── agents/                # AI agents for various tasks
├── db/                    # Database models and session
├── schemas/               # API request/response models
└── requirements.txt       # Python dependencies
```

## 🎯 Usage Examples

### Mood Entry
User: "I'm feeling anxious about my presentation tomorrow"
Response: Personalized acknowledgment + mood analysis + reflection question + progress summary

### Small Talk
User: "Hello, how are you?"
Response: Friendly greeting without mood analysis

### Off-Topic
User: "What's the weather like?"
Response: Polite redirection to mental well-being topics

## 🔮 Future Enhancements

- Multi-user support with authentication
- Voice chat capabilities
- Mood trend visualizations
- Integration with external mental health resources
- Advanced conversation memory and context 