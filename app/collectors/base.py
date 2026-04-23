from dataclasses import dataclass
from datetime import datetime


@dataclass
class NormalizedQuote:
    source: str
    market_hash_name: str
    display_name: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    bid_price: float
    ask_price: float
    volume: float


class BaseCollector:
    source_name: str = "base"

    async def fetch_history(self, market_hash_name: str, limit: int = 120) -> list[NormalizedQuote]:
        raise NotImplementedError
