
reflection_prompt = """
    "The user just wrote a journal entry with a **{mood}** mood.\n"
    "Here are their last journal entries:\n"
    "{past_entries}\n\n"
    "Ask the user a single, thoughtful, empathetic question that encourages self-reflection, "
    "based on their current mood and recent thoughts."
"""