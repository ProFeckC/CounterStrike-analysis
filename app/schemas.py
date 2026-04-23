from datetime import datetime

from pydantic import BaseModel, Field


class ItemRead(BaseModel):
    id: int
    market_hash_name: str
    display_name: str
    game: str

    model_config = {"from_attributes": True}


class CandleRead(BaseModel):
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    bid_price: float
    ask_price: float
    volume: float

    model_config = {"from_attributes": True}


class SignalRead(BaseModel):
    signal_type: str
    score: float
    action: str
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SummaryRead(BaseModel):
    item: str
    source: str
    last_close: float | None = None
    ma5: float | None = None
    ma20: float | None = None
    rsi14: float | None = None
    trend_bias: str
    suggested_action: str
    explanation: str


class IngestResponse(BaseModel):
    source: str
    item: str
    candles_inserted: int = Field(ge=0)
