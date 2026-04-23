from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


ALIASES_PATH = Path(__file__).resolve().parent.parent / "data" / "item_aliases.json"


def resolve_item_input(item_name: str, source: str) -> tuple[str, str]:
    cleaned = item_name.strip()
    aliases = load_item_aliases()
    resolved = aliases.get(_normalize_name(cleaned))
    if resolved:
        return resolved, cleaned

    if source == "youpin" and _looks_like_chinese(cleaned):
        raise ValueError(
            "未找到这个中文饰品名的映射。请先在 app/data/item_aliases.json 里补充中文名到 Steam 英文 market_hash_name 的对应关系。"
        )

    return cleaned, cleaned


@lru_cache
def load_item_aliases() -> dict[str, str]:
    if not ALIASES_PATH.exists():
        return {}

    raw = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    return {_normalize_name(key): value for key, value in raw.items()}


def _normalize_name(value: str) -> str:
    normalized = (
        value.strip()
        .replace("（", "(")
        .replace("）", ")")
        .replace("【", "[")
        .replace("】", "]")
        .replace("｜", "|")
        .replace("、", " ")
    )
    return " ".join(normalized.split()).lower()


def _looks_like_chinese(value: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in value)
