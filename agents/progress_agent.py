from agno.agent import Agent
from agno.models.openai import OpenAIChat
from db.crud import get_last_journal_entries
from agents.prompts.progress import progress_prompt
model = OpenAIChat(id="gpt-4o-mini")

agent = Agent(
    model=model,
    description="You analyze multiple journal entries and give a 1-2 sentence progress summary and a progress score from 0 to 1.",
)

async def get_progress_summary(db, user_id: str):
    entries = await get_last_journal_entries(db, user_id=user_id, limit=5)
    if not entries:
        return {"summary": None, "score": None}

    formatted = "\n".join(f"- {e.text} (Mood: {e.mood})" for e in entries)

    formatted_prompt = progress_prompt.format(formatted=formatted)
    response = await agent.arun(formatted_prompt)
    if hasattr(response, 'content'):
        lines = response.content.strip().split("\n")
    else:
        lines = str(response).strip().split("\n")

    summary = lines[0]
    score = None
    for line in lines[1:]:
        if "score" in line.lower():
            try:
                score = float("".join(filter(lambda c: c.isdigit() or c == ".", line)))
            except:
                pass

    return {"summary": summary, "score": score}
