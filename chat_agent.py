import chainlit as cl
from agno.agent import Agent
from agno.models.openai import OpenAIChat

model = OpenAIChat(id="gpt-4o-mini")

agent = Agent(
    model=model,
    description="You are a reflection mood agent. Respond with a thoughtful question that helps the user reflect on why they might be feeling this way. The question should be empathetic and encourage self-reflection.",
    markdown=False
)

@cl.on_message
async def main(message: cl.Message):
    mood = message.content.strip().lower()

    # Create a simple reflection question without database context
    prompt = f"""You are a reflection mood agent. The user is feeling {mood}.
    
    Respond with a thoughtful question that helps the user reflect on why they might be feeling this way. 
    The question should be empathetic and encourage self-reflection.
    
    Question:"""
    
    response = await agent.arun(prompt)
    question = response.content if hasattr(response, "content") else str(response)
    
    await cl.Message(content=question).send()
