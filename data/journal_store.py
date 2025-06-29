from datetime import datetime
from typing import List, Dict

journal_entries: List[Dict] = []

def save_entry(user_id: str, text: str, mood: str, sentiment_score: float):
    journal_entries.append({
        "user_id": user_id,
        "text": text,
        "mood": mood,
        "sentiment_score": sentiment_score,
        "timestamp": datetime.utcnow().isoformat()
    })

def get_entries(user_id: str) -> List[Dict]:
    return [entry for entry in journal_entries if entry["user_id"] == user_id]
