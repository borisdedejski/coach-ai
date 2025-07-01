from agents.reflection_agent import get_reflection_question

# Test different moods
test_moods = ["happy", "sad", "anxious", "stressed", "motivated", "angry"]

print("Testing reflection questions for different moods:\n")

for mood in test_moods:
    try:
        question = get_reflection_question(mood)
        print(f"Mood: {mood}")
        print(f"Reflection Question: {question}")
        print("-" * 50)
    except Exception as e:
        print(f"Error with mood '{mood}': {e}")
        print("-" * 50) 