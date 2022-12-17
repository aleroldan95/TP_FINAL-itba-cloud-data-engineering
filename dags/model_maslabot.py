"""Dummy data model definition."""

from sqlalchemy import Column, Integer, String, Date, Float, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StockValue(Base):
    """Stock value data model."""

    __tablename__ = "masla_tweets"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    text = Column(String)
    __table_args__ = (UniqueConstraint("id", "date"),)

    def __repr__(self):
        return f"<MaslaTweet(date='{self.date}', text='{self.text}')>"
