"""Dummy data model definition."""

from sqlalchemy import Column, Integer, String, Date, Float, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StockValue(Base):
    """Stock value data model."""

    __tablename__ = "stock_value"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    symbol = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    __table_args__ = (UniqueConstraint("date", "symbol"),)

    def __repr__(self):
        return f"<StockValue(date='{self.date}', symbol='{self.symbol}', close={self.close})>"
