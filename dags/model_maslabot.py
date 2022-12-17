"""Dummy data model definition."""

from sqlalchemy import Column, Integer, String, Date, Float, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TweetTable(Base):
    """TweetBase data model."""

    __tablename__ = "masla_tweets"
    id = Column(String, primary_key=True)
    date = Column(Date)
    text = Column(String)
    __table_args__ = (UniqueConstraint("id", "date"),)

    def __repr__(self):
        return f"<MaslaTweet(date='{self.date}', text='{self.text}')>"

class SentimentTable(Base):
    """TweetBase data model."""

    __tablename__ = "masla_sentiment"
    id = Column(String, primary_key=True)
    sentiment = Column(String)
    __table_args__ = (UniqueConstraint("id", "sentiment"),)

    def __repr__(self):
        return f"<MaslaTweet(date='{self.date}', sentiment='{self.sentiment}')>"
