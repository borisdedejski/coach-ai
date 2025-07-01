from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    text = Column(String)
    mood = Column(String)
    sentiment_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    reflection_question = Column(String, nullable=True)
    progress_summary = Column(String, nullable=True)
    progress_score = Column(Float, nullable=True)
