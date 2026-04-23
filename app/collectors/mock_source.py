from __future__ import annotations

from datetime import datetime, timedelta
import math
import random

from app.collectors.base import BaseCollector, NormalizedQuote


class MockCollector(BaseCollector):
    source_name = "mock"

    async def fetch_history(self, market_hash_name: str, limit: int = 120) -> list[NormalizedQuote]:
        random.seed(market_hash_name)
        base_price = random.uniform(30, 300)
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        rows: list[NormalizedQuote] = []

        for idx in range(limit):
            ts = now - timedelta(hours=limit - idx)
            wave = math.sin(idx / 7) * base_price * 0.03
            drift = idx * base_price * 0.0009
            noise = random.uniform(-base_price * 0.012, base_price * 0.012)
            close_price = max(1.0, base_price + wave + drift + noise)
            open_price = max(1.0, close_price + random.uniform(-2.2, 2.2))
            high_price = max(open_price, close_price) + random.uniform(0.2, 3.0)
            low_price = max(0.1, min(open_price, close_price) - random.uniform(0.2, 3.0))
            spread = max(0.1, close_price * 0.01)
            bid_price = max(0.1, close_price - spread / 2)
            ask_price = close_price + spread / 2
            volume = random.uniform(5, 60)

            rows.append(
                NormalizedQuote(
                    source=self.source_name,
                    market_hash_name=market_hash_name,
                    display_name=market_hash_name,
                    timestamp=ts,
                    open_price=round(open_price, 2),
                    high_price=round(high_price, 2),
                    low_price=round(low_price, 2),
                    close_price=round(close_price, 2),
                    bid_price=round(bid_price, 2),
                    ask_price=round(ask_price, 2),
                    volume=round(volume, 2),
                )
            )

        return rows
