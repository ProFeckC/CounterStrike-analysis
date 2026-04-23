from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector
from app.collectors.cs2sh import CS2SHCollector
from app.collectors.mock_source import MockCollector
from app.models import Item, MarketQuote, TradeSignal
from app.services.item_aliases import resolve_item_input
from app.services.indicators import compute_indicators
from app.services.signals import build_signal_from_frame


def get_collector(source: str) -> BaseCollector:
    mapping: dict[str, BaseCollector] = {
        "mock": MockCollector(),
        "cs2sh": CS2SHCollector(),
        "youpin": CS2SHCollector(),
    }
    if source not in mapping:
        raise ValueError(f"Unsupported source: {source}")
    return mapping[source]


async def ingest_quotes(db: Session, source: str, market_hash_name: str, limit: int = 120) -> int:
    collector = get_collector(source)
    resolved_name, display_name = resolve_item_input(market_hash_name, source=source)
    quotes = await collector.fetch_history(market_hash_name=resolved_name, limit=limit)
    if not quotes:
        return 0

    item = db.scalar(select(Item).where(Item.market_hash_name == resolved_name))
    if item is None:
        item = Item(
            market_hash_name=resolved_name,
            display_name=display_name or quotes[0].display_name,
            game="cs2",
        )
        db.add(item)
        db.flush()
    elif display_name and item.display_name != display_name:
        item.display_name = display_name

    inserted = 0
    existing_ts = {
        row[0]
        for row in db.execute(
            select(MarketQuote.timestamp).where(
                MarketQuote.item_id == item.id,
                MarketQuote.source == source,
            )
        ).all()
    }

    for quote in quotes:
        if quote.timestamp in existing_ts:
            continue
        db.add(
            MarketQuote(
                source=quote.source,
                item_id=item.id,
                timestamp=quote.timestamp,
                open_price=quote.open_price,
                high_price=quote.high_price,
                low_price=quote.low_price,
                close_price=quote.close_price,
                bid_price=quote.bid_price,
                ask_price=quote.ask_price,
                volume=quote.volume,
            )
        )
        inserted += 1

    db.flush()
    refresh_latest_signal(db=db, item_id=item.id, source=source)
    db.commit()
    return inserted


def refresh_latest_signal(db: Session, item_id: int, source: str) -> None:
    quotes = db.execute(
        select(MarketQuote)
        .where(MarketQuote.item_id == item_id, MarketQuote.source == source)
        .order_by(MarketQuote.timestamp.asc())
    ).scalars().all()

    if not quotes:
        return

    import pandas as pd

    frame = pd.DataFrame(
        [
            {
                "timestamp": quote.timestamp,
                "close_price": quote.close_price,
            }
            for quote in quotes
        ]
    )
    frame = compute_indicators(frame)
    signal = build_signal_from_frame(frame)

    db.query(TradeSignal).filter(
        TradeSignal.item_id == item_id,
        TradeSignal.source == source,
    ).delete()

    db.add(
        TradeSignal(
            item_id=item_id,
            source=source,
            signal_type=signal["signal_type"],
            score=signal["score"],
            action=signal["action"],
            reason=signal["explanation"],
        )
    )
