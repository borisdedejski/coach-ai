from agno.agent import Agent
from agno.models.openai import OpenAIChat
from db.crud import get_last_journal_entries, get_user_entries_for_analysis
from agents.prompts.progress import enhanced_progress_prompt
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple, Optional
from agents.prompts.progress import description_prompt

model = OpenAIChat(id="gpt-4o-mini")

agent = Agent(
    model=model,
    description=description_prompt
)

def analyze_mood_by_day_of_week(entries: List) -> Dict[str, Dict]:
    """Analyze mood patterns by day of the week"""
    day_moods = defaultdict(list)
    day_sentiments = defaultdict(list)
    
    for entry in entries:
        day_name = entry.timestamp.strftime('%A')  # Monday, Tuesday, etc.
        day_moods[day_name].append(entry.mood)
        day_sentiments[day_name].append(entry.sentiment_score)
    
    analysis = {}
    for day, moods in day_moods.items():
        if len(moods) >= 2:  # Only analyze if we have at least 2 entries for that day
            avg_sentiment = sum(day_sentiments[day]) / len(day_sentiments[day])
            most_common_mood = Counter(moods).most_common(1)[0][0]
            analysis[day] = {
                'avg_sentiment': avg_sentiment,
                'most_common_mood': most_common_mood,
                'entry_count': len(moods)
            }
    
    return analysis

def analyze_mood_trends(entries: List, window_size: int = 7) -> Dict:
    """Analyze mood trends over time using sliding window"""
    if len(entries) < window_size:
        return {"trend": "insufficient_data", "direction": "stable"}
    
    # Sort entries by timestamp (oldest first)
    sorted_entries = sorted(entries, key=lambda x: x.timestamp)
    
    # Calculate moving average
    sentiments = [e.sentiment_score for e in sorted_entries]
    moving_avg = []
    
    for i in range(len(sentiments) - window_size + 1):
        window_avg = sum(sentiments[i:i+window_size]) / window_size
        moving_avg.append(window_avg)
    
    if len(moving_avg) < 2:
        return {"trend": "insufficient_data", "direction": "stable"}
    
    # Determine trend direction
    first_avg = moving_avg[0]
    last_avg = moving_avg[-1]
    change = last_avg - first_avg
    
    if change > 0.1:
        direction = "improving"
    elif change < -0.1:
        direction = "declining"
    else:
        direction = "stable"
    
    return {
        "trend": "analyzed",
        "direction": direction,
        "change_magnitude": abs(change),
        "first_avg": first_avg,
        "last_avg": last_avg
    }

def detect_triggers(entries: List) -> Dict:
    """Detect common themes and triggers in journal entries"""
    # Common emotional triggers and themes
    trigger_keywords = {
        'work_stress': ['work', 'job', 'boss', 'deadline', 'meeting', 'office', 'colleague'],
        'relationship': ['partner', 'boyfriend', 'girlfriend', 'husband', 'wife', 'friend', 'family'],
        'health': ['sick', 'pain', 'doctor', 'medicine', 'sleep', 'exercise', 'diet'],
        'financial': ['money', 'bills', 'expenses', 'budget', 'debt', 'salary'],
        'social': ['party', 'social', 'lonely', 'people', 'crowd', 'conversation'],
        'personal_goals': ['goal', 'achievement', 'success', 'failure', 'progress', 'plan']
    }
    
    all_text = ' '.join([entry.text.lower() for entry in entries])
    trigger_counts = {}
    
    for trigger_type, keywords in trigger_keywords.items():
        count = sum(1 for keyword in keywords if keyword in all_text)
        if count > 0:
            trigger_counts[trigger_type] = count
    
    # Find most frequent triggers
    most_frequent = []
    if trigger_counts:
        sorted_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)
        most_frequent = [trigger for trigger, count in sorted_triggers[:3] if count >= 2]
    
    return {
        "detected_triggers": trigger_counts,
        "most_frequent": most_frequent,
        "total_entries_analyzed": len(entries)
    }

def calculate_overall_mood_direction(entries: List) -> Dict:
    """Calculate overall mood direction and stability"""
    if len(entries) < 3:
        return {"direction": "insufficient_data", "stability": "unknown"}
    
    sentiments = [e.sentiment_score for e in entries]
    
    # Calculate trend
    first_third = sum(sentiments[:len(sentiments)//3]) / (len(sentiments)//3)
    last_third = sum(sentiments[-len(sentiments)//3:]) / (len(sentiments)//3)
    
    change = last_third - first_third
    
    if change > 0.15:
        direction = "significantly_improving"
    elif change > 0.05:
        direction = "slightly_improving"
    elif change < -0.15:
        direction = "significantly_declining"
    elif change < -0.05:
        direction = "slightly_declining"
    else:
        direction = "stable"
    
    # Calculate stability (variance)
    mean_sentiment = sum(sentiments) / len(sentiments)
    variance = sum((s - mean_sentiment) ** 2 for s in sentiments) / len(sentiments)
    
    if variance < 0.1:
        stability = "very_stable"
    elif variance < 0.25:
        stability = "moderately_stable"
    else:
        stability = "volatile"
    
    return {
        "direction": direction,
        "stability": stability,
        "overall_change": change,
        "variance": variance
    }

async def get_progress_summary(db, user_id: str):
    """Enhanced progress summary with deeper personalization"""
    # Get more entries for comprehensive analysis
    entries = await get_user_entries_for_analysis(db, user_id=user_id, limit=20)
    
    if not entries:
        return {"summary": None, "score": None, "patterns": None}
    
    # Perform various analyses
    day_patterns = analyze_mood_by_day_of_week(entries)
    trend_analysis = analyze_mood_trends(entries)
    trigger_analysis = detect_triggers(entries)
    mood_direction = calculate_overall_mood_direction(entries)
    
    # Prepare recent entries for LLM analysis
    recent_entries = entries[:5]  # Last 5 entries for immediate context
    formatted_recent = "\n".join(f"- {e.text} (Mood: {e.mood}, Score: {e.sentiment_score:.2f})" for e in recent_entries)
    
    # Create comprehensive analysis context
    analysis_context = {
        "day_patterns": day_patterns,
        "trend_analysis": trend_analysis,
        "trigger_analysis": trigger_analysis,
        "mood_direction": mood_direction,
        "total_entries": len(entries)
    }
    
    # Format the enhanced prompt
    formatted_prompt = enhanced_progress_prompt.format(
        formatted=formatted_recent,
        day_patterns=str(day_patterns),
        trend_analysis=str(trend_analysis),
        trigger_analysis=str(trigger_analysis),
        mood_direction=str(mood_direction)
    )
    
    response = await agent.arun(formatted_prompt)
    
    if hasattr(response, 'content'):
        lines = response.content.strip().split("\n")
    else:
        lines = str(response).strip().split("\n")

    summary = lines[0] if lines else "No summary available"
    score = None
    
    # Extract score from response
    for line in lines[1:]:
        if "score" in line.lower():
            try:
                score = float("".join(filter(lambda c: c.isdigit() or c == ".", line)))
                break
            except:
                pass
    
    return {
        "summary": summary, 
        "score": score,
        "patterns": analysis_context
    }
