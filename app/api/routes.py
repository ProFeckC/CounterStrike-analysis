from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Item, MarketQuote, TradeSignal
from app.schemas import CandleRead, IngestResponse, ItemRead, SignalRead, SummaryRead
from app.services.indicators import compute_indicators
from app.services.ingest import ingest_quotes
from app.services.signals import build_signal_from_frame


router = APIRouter(prefix="/api/v1", tags=["market-analysis"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ingest/mock", response_model=IngestResponse)
async def ingest_mock_data(
    item_name: str = Query(default="AK-47 | 红线（久经沙场）"),
    limit: int = Query(default=120, ge=30, le=1000),
    db: Session = Depends(get_db),
):
    inserted = await ingest_quotes(db=db, source="mock", market_hash_name=item_name, limit=limit)
    return IngestResponse(source="mock", item=item_name, candles_inserted=inserted)


@router.post("/ingest/{source}", response_model=IngestResponse)
async def ingest_source_data(
    source: str,
    item_name: str = Query(...),
    limit: int = Query(default=120, ge=30, le=1000),
    db: Session = Depends(get_db),
):
    try:
        inserted = await ingest_quotes(db=db, source=source, market_hash_name=item_name, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    return IngestResponse(source=source, item=item_name, candles_inserted=inserted)


@router.get("/items", response_model=list[ItemRead])
def list_items(db: Session = Depends(get_db)):
    rows = db.execute(select(Item).order_by(Item.id.desc())).scalars().all()
    return rows


@router.get("/items/{item_id}/candles", response_model=list[CandleRead])
def get_item_candles(
    item_id: int,
    source: str = Query(default="mock"),
    limit: int = Query(default=120, ge=1, le=2000),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(MarketQuote)
        .where(MarketQuote.item_id == item_id, MarketQuote.source == source)
        .order_by(MarketQuote.timestamp.desc())
        .limit(limit)
    ).scalars().all()
    return list(reversed(rows))


@router.get("/items/{item_id}/signals", response_model=list[SignalRead])
def get_item_signals(
    item_id: int,
    source: str = Query(default="mock"),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(TradeSignal)
        .where(TradeSignal.item_id == item_id, TradeSignal.source == source)
        .order_by(TradeSignal.created_at.desc())
    ).scalars().all()
    return rows


@router.get("/items/{item_id}/summary", response_model=SummaryRead)
def get_item_summary(
    item_id: int,
    source: str = Query(default="mock"),
    db: Session = Depends(get_db),
):
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    quotes = db.execute(
        select(MarketQuote)
        .where(MarketQuote.item_id == item_id, MarketQuote.source == source)
        .order_by(MarketQuote.timestamp.asc())
    ).scalars().all()
    if not quotes:
        raise HTTPException(status_code=404, detail="No market data found for this item and source")

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
    latest = frame.iloc[-1]

    return SummaryRead(
        item=item.display_name,
        source=source,
        last_close=_safe_value(latest.get("close_price")),
        ma5=_safe_value(latest.get("ma5")),
        ma20=_safe_value(latest.get("ma20")),
        rsi14=_safe_value(latest.get("rsi14")),
        trend_bias=signal["trend_bias"],
        suggested_action=signal["action"],
        explanation=signal["explanation"],
    )


def _safe_value(value):
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    return float(value) if value is not None else None
