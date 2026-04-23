from __future__ import annotations

import pandas as pd


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    frame = df.sort_values("timestamp").copy()
    frame["ma5"] = frame["close_price"].rolling(window=5).mean()
    frame["ma20"] = frame["close_price"].rolling(window=20).mean()
    frame["ema12"] = frame["close_price"].ewm(span=12, adjust=False).mean()
    frame["ema26"] = frame["close_price"].ewm(span=26, adjust=False).mean()
    frame["macd"] = frame["ema12"] - frame["ema26"]
    frame["signal_line"] = frame["macd"].ewm(span=9, adjust=False).mean()
    frame["rsi14"] = _compute_rsi(frame["close_price"], period=14)
    return frame


def _compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)
