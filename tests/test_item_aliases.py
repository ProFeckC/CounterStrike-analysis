from app.services.item_aliases import resolve_item_input


def test_resolve_known_youpin_chinese_alias():
    market_hash_name, display_name = resolve_item_input("AK-47 | 红线（久经沙场）", source="youpin")
    assert market_hash_name == "AK-47 | Redline (Field-Tested)"
    assert display_name == "AK-47 | 红线（久经沙场）"


def test_keep_english_name_for_mock():
    market_hash_name, display_name = resolve_item_input("AK-47 | Redline (Field-Tested)", source="mock")
    assert market_hash_name == "AK-47 | Redline (Field-Tested)"
    assert display_name == "AK-47 | Redline (Field-Tested)"
