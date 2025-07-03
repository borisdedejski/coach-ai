import streamlit as st
import requests
import pandas as pd
from datetime import datetime

BASE_URL = "http://localhost:8000/v1"
USER_ID = "123"  # You can later make this dynamic

st.set_page_config(page_title="AI Coach Journal", layout="centered")
st.title("🧠 AI Coach Journal")

# Sidebar for navigation
page = st.sidebar.radio("Navigate", ["New Entry", "History", "Insights"])

if page == "New Entry":
    st.subheader("📔 Write a Journal Entry")
    text = st.text_area("How are you feeling today?", height=200)

    if st.button("Submit"):
        if not text.strip():
            st.warning("Please write something before submitting.")
        else:
            with st.spinner("Analyzing..."):
                res = requests.post(f"{BASE_URL}/chat", json={"text": text, "user_id": USER_ID})

            if res.status_code == 200:
                data = res.json()
                st.success(f"**Response:** {data['reply']}")
                st.info(f"**Intent:** {data['intent']}")
                
                # Only show mood-related info if it's a mood-related response
                if data.get('mood'):
                    st.success(f"Mood detected: **{data['mood']}** (score: {data['sentiment_score']:.2f})")
                    st.markdown(f"**Reflection Question:** {data['reflection_question']}")
                    st.markdown(f"**Progress Summary:** {data['progress_summary']}")
                    st.markdown(f"**Progress Score:** {data['progress_score']:.2f}")
            else:
                st.error("Something went wrong with the request.")

elif page == "History":
    st.subheader("📜 Journal History")
    res = requests.get(f"{BASE_URL}/history", params={"user_id": USER_ID})

    if res.status_code == 200:
        entries = res.json()
        for entry in entries:
            st.markdown(f"### {entry['timestamp'][:10]}")
            st.markdown(f"- **Text:** {entry['text']}")
            st.markdown(f"- **Mood:** {entry['mood']} ({entry['sentiment_score']:.2f})")
            st.markdown(f"- **Reflection:** {entry['reflection_question']}")
            st.markdown("---")
    else:
        st.error("Could not fetch history.")

elif page == "Insights":
    st.subheader("📈 Insights")
    res = requests.get(f"{BASE_URL}/insights", params={"user_id": USER_ID})

    if res.status_code == 200:
        data = res.json()
        st.markdown(f"**Average Sentiment Score:** {data['average_sentiment_score']:.2f}")
        st.markdown(f"**Most Common Mood:** {data['most_common_mood']}")
        st.markdown(f"**Mood Trend:** {data['mood_trend']}")
        st.markdown(f"**Entry Streak:** {data['entry_streak_days']} days")
        st.markdown(f"**Total Entries:** {data['total_entries']}")
        
        if data['progress_trend']:
            df = pd.DataFrame(data['progress_trend'])
            df['date'] = pd.to_datetime(df['date'])
            st.line_chart(df.set_index('date')['progress_score'])
        else:
            st.info("No progress data available yet.")
    else:
        st.error("Failed to load insights.")
