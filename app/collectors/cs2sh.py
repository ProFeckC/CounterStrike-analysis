from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx

from app.collectors.base import BaseCollector, NormalizedQuote
from app.config import get_settings


class CS2SHCollector(BaseCollector):
    source_name = "youpin"

    async def fetch_history(self, market_hash_name: str, limit: int = 120) -> list[NormalizedQuote]:
        settings = get_settings()
        if not settings.cs2sh_api_key:
            raise ValueError("CS2SH_API_KEY 为空。请先在 .env 里配置 cs2.sh 的 API Key，再使用 youpin 数据源。")

        start, interval = _build_history_range(limit)
        payload = {
            "items": [market_hash_name],
            "start": start,
            "end": "now",
            "sources": ["youpin"],
            "interval": interval,
        }
        headers = {
            "Authorization": f"Bearer {settings.cs2sh_api_key}",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.cs2sh_base_url.rstrip('/')}/v1/prices/history",
                json=payload,
                headers=headers,
            )

        if response.status_code == 401:
            raise ValueError("cs2.sh API Key 无效或缺失，请检查 .env 中的 CS2SH_API_KEY。")
        response.raise_for_status()
        body = response.json()
        item_payload = (body.get("items") or {}).get(market_hash_name)
        if not item_payload:
            raise ValueError(f"未在 youpin 返回中找到饰品：{market_hash_name}")

        rows: list[NormalizedQuote] = []
        for bucket in item_payload.get("data", []):
            youpin = bucket.get("youpin")
            if not youpin:
                continue
            rows.append(
                NormalizedQuote(
                    source=self.source_name,
                    market_hash_name=market_hash_name,
                    display_name=market_hash_name,
                    timestamp=datetime.fromisoformat(bucket["bucket"].replace("Z", "+00:00")).replace(tzinfo=None),
                    open_price=float(youpin.get("open_ask") or youpin.get("close_ask") or 0.0),
                    high_price=float(youpin.get("high_ask") or youpin.get("close_ask") or 0.0),
                    low_price=float(youpin.get("low_ask") or youpin.get("close_ask") or 0.0),
                    close_price=float(youpin.get("close_ask") or youpin.get("open_ask") or 0.0),
                    bid_price=float(youpin.get("close_bid") or 0.0),
                    ask_price=float(youpin.get("close_ask") or 0.0),
                    volume=float(youpin.get("ask_volume") or youpin.get("sample_count") or 0.0),
                )
            )

        if not rows:
            raise ValueError(f"youpin 没有返回可用的历史行情：{market_hash_name}")

        return rows


def _build_history_range(limit: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    if limit <= 336:
        return (now - timedelta(hours=limit)).date().isoformat(), "1h"
    return (now - timedelta(days=limit)).date().isoformat(), "1d"
