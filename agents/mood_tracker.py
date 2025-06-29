from textblob import TextBlob

def analyze_mood(text: str) -> dict:
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity  # -1 (negative) to +1 (positive)

    # Basic mood classification
    if sentiment > 0.4:
        mood = "positive"
    elif sentiment < -0.4:
        mood = "negative"
    else:
        mood = "neutral"

    return {"mood": mood, "sentiment_score": sentiment}
