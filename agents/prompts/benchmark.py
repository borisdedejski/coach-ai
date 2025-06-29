comparison_prompt = """Compare these two answers to the same question and evaluate their similarity on a scale from 0 to 1, where 1 means identical in meaning and 0 means completely different. Provide a brief explanation.

System Answer: {system_answer}
Reference Answer: {reference_answer}

Return the response in the following JSON format:
{{"similarity_score": float, "explanation": string}}
"""
