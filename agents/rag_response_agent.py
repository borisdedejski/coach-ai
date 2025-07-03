from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agents.rag.retriever import RAGRetriever
from agents.prompts.rag_response import rag_agent_description, rag_response_prompt
from typing import Dict, Any, Optional

rag_retriever = RAGRetriever()
model = OpenAIChat(id="gpt-4o-mini")

rag_response_agent = Agent(
    model=model,
    description=rag_agent_description,
    markdown=False
)

def generate_rag_response(
    user_message: str, 
    user_context: str = "", 
    mood_info: Optional[Dict[str, Any]] = None,
    use_knowledge_base: bool = True
) -> Dict[str, Any]:
    """
    Generate a RAG-enhanced response using knowledge base retrieval
    
    Args:
        user_message: The user's message
        user_context: Additional context about the user (e.g., history, mood trends)
        mood_info: Current mood analysis if available
        use_knowledge_base: Whether to use knowledge base retrieval
        
    Returns:
        Dictionary containing response and metadata
    """
    
    # Get relevant knowledge base context
    knowledge_context = ""
    similarity_score = 0.0
    retrieved_chunks = []
    
    if use_knowledge_base:
        try:
            retrieved_chunks = rag_retriever.retrieve_relevant_chunks(user_message, top_k=2)
            similarity_score = rag_retriever.get_similarity_score(user_message)
            
            if retrieved_chunks:
                knowledge_context = rag_retriever.get_context_for_response(user_message)
        except Exception as e:
            print(f"Warning: Knowledge base retrieval failed: {e}")
    
    # Build the prompt
    mood_info_text = ""
    if mood_info:
        mood_info_text = f"Current Mood Analysis:\n- Mood: {mood_info.get('mood', 'unknown')}\n- Sentiment Score: {mood_info.get('sentiment_score', 0.0):.2f}"
    
    full_prompt = rag_response_prompt.format(
        knowledge_context=knowledge_context,
        user_context=user_context,
        mood_info=mood_info_text,
        user_message=user_message
    )
    
    # Generate response
    response = rag_response_agent.run(full_prompt)
    
    return {
        "response": response.content if hasattr(response, 'content') else str(response),
        "knowledge_context": knowledge_context,
        "similarity_score": similarity_score,
        "retrieved_chunks": retrieved_chunks,
        "used_knowledge_base": use_knowledge_base and bool(retrieved_chunks)
    }

def generate_mood_specific_response(
    user_message: str, 
    mood: str, 
    sentiment_score: float,
    user_context: str = ""
) -> Dict[str, Any]:
    """
    Generate a mood-specific RAG response
    
    Args:
        user_message: The user's message
        mood: Detected mood
        sentiment_score: Sentiment score
        user_context: Additional user context
        
    Returns:
        Dictionary containing response and metadata
    """
    
    mood_info = {
        "mood": mood,
        "sentiment_score": sentiment_score
    }
    
    if sentiment_score < 0:
        enhanced_query = f"coping strategies for {mood} feelings"
        try:
            coping_chunks = rag_retriever.retrieve_relevant_chunks(enhanced_query, top_k=1)
            if coping_chunks:
                user_message += f"\n\n[Looking for coping strategies for {mood} feelings]"
        except:
            pass
    
    return generate_rag_response(
        user_message=user_message,
        user_context=user_context,
        mood_info=mood_info,
        use_knowledge_base=True
    ) 