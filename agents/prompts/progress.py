enhanced_progress_prompt = """
Here are recent journal entries:
{formatted}

Based on the following detailed analysis, provide a comprehensive 2-3 sentence summary of the user's emotional progress:

**Day-of-Week Patterns:** {day_patterns}
**Trend Analysis:** {trend_analysis}
**Trigger Analysis:** {trigger_analysis}
**Mood Direction:** {mood_direction}

Your summary should include:
1. Overall emotional direction (improving/declining/stable)
2. Any notable day-of-week patterns (e.g., "You seem more anxious on Mondays")
3. Key triggers or themes affecting mood
4. Specific insights about mood stability and changes

Then provide a numeric progress score from 0 (no progress) to 1 (very good progress).

Focus on being personal and actionable in your insights.
"""

description_prompt = """
You analyze multiple journal entries and provide detailed emotional progress insights including patterns, trends, and triggers.
"""