from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    market_hash_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), index=True)
    game: Mapped[str] = mapped_column(String(50), default="cs2")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quotes: Mapped[list["MarketQuote"]] = relationship(back_populates="item", cascade="all, delete-orphan")
    signals: Mapped[list["TradeSignal"]] = relationship(back_populates="item", cascade="all, delete-orphan")


class MarketQuote(Base):
    __tablename__ = "market_quotes"
    __table_args__ = (
        UniqueConstraint("source", "item_id", "timestamp", name="uq_quote_source_item_ts"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    open_price: Mapped[float] = mapped_column(Float)
    high_price: Mapped[float] = mapped_column(Float)
    low_price: Mapped[float] = mapped_column(Float)
    close_price: Mapped[float] = mapped_column(Float, index=True)
    bid_price: Mapped[float] = mapped_column(Float, default=0.0)
    ask_price: Mapped[float] = mapped_column(Float, default=0.0)
    volume: Mapped[float] = mapped_column(Float, default=0.0)

    item: Mapped["Item"] = relationship(back_populates="quotes")


class TradeSignal(Base):
    __tablename__ = "trade_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    signal_type: Mapped[str] = mapped_column(String(50), index=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    action: Mapped[str] = mapped_column(String(20), index=True)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    item: Mapped["Item"] = relationship(back_populates="signals")
