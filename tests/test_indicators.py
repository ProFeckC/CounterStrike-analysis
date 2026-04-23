import pandas as pd

from app.services.indicators import compute_indicators
from app.services.signals import build_signal_from_frame


def test_compute_indicators_and_signal():
    rows = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=40, freq="h"),
            "close_price": [100 + idx * 0.8 for idx in range(40)],
        }
    )
    frame = compute_indicators(rows)
    signal = build_signal_from_frame(frame)

    assert "ma5" in frame.columns
    assert "rsi14" in frame.columns
    assert signal["action"] in {"buy_watch", "hold", "sell_watch"}
