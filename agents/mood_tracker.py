import os
import json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agents.prompts.mood import mood_analysis_prompt

model = OpenAIChat(id="gpt-4o-mini")

agent = Agent(
    model=model,
    description="You are a mood analyzer. Return a JSON with 'mood' and 'sentiment_score' (-1 to 1).",
    markdown=False
)

def analyze_mood(text: str) -> dict:
    prompt = mood_analysis_prompt.format(entry=text)
    response = agent.run(prompt)
    try:
        return json.loads(response.content.strip())
    except Exception:
        return {"mood": "neutral", "sentiment_score": 0.0}
