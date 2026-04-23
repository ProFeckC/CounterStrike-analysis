from __future__ import annotations

from app.collectors.base import BaseCollector, NormalizedQuote
from app.config import get_settings


class CS2SHCollector(BaseCollector):
    source_name = "cs2sh"

    async def fetch_history(self, market_hash_name: str, limit: int = 120) -> list[NormalizedQuote]:
        settings = get_settings()
        if not settings.cs2sh_api_key:
            raise ValueError("CS2SH_API_KEY is empty. Please set it in your .env before using the cs2sh collector.")

        raise NotImplementedError(
            "The cs2sh collector is a placeholder in this MVP. Add request parsing here once you confirm the API contract you want to use."
        )
