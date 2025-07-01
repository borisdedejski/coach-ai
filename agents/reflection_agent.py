from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sqlalchemy.ext.asyncio import AsyncSession
from agents.prompts.reflection import reflection_prompt
from db.crud import get_last_journal_entries

model = OpenAIChat(id="gpt-4o-mini")

agent = Agent(
    model=model,
    description="You are a reflection mood agent. Respond with a thoughtful question that helps the user reflect on why they might be feeling this way. The question should be empathetic and encourage self-reflection.",
    markdown=False
)

async def get_reflection_question(db: AsyncSession, user_id: str, mood: str) -> str:
    past_entries = await get_last_journal_entries(db, user_id=user_id, limit=3)
    context = "\n".join(f"- {entry.text} ({entry.mood})" for entry in past_entries)

    prompt = reflection_prompt.format(
        mood=mood.lower(),
        past_entries=context
    )

    response = await agent.arun(prompt)
    return response.content if hasattr(response, 'content') else str(response)
