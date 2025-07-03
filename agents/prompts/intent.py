# Intent classification prompts

intent_prompt = '''
Classify this message into:
- "small_talk" → Greetings or casual chat.
- "off_topic" → Unrelated topics (sports, tech, cars, etc.).
- "mood_entry" → Emotional or mood-related sharing.

Message: "{message}"

Only reply with one of: "small_talk", "off_topic", or "mood_entry".
'''

intent_with_history_prompt = '''
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
''' 