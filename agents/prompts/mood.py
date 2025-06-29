mood_analysis_prompt = """
Analyze the following journal entry and return:
- The mood (e.g., happy, anxious, sad, motivated, stressed)
- A sentiment score from -1 (very negative) to 1 (very positive)

Entry:
{entry}

Respond in JSON like:
{{
  "mood": "happy",
  "sentiment_score": 0.7
}}
"""
