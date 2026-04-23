from __future__ import annotations

import math

import pandas as pd


def build_signal_from_frame(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {
            "signal_type": "no_data",
            "score": 0.0,
            "action": "hold",
            "trend_bias": "neutral",
            "explanation": "暂无可用行情数据。",
        }

    latest = frame.iloc[-1]
    ma5 = _safe_float(latest.get("ma5"))
    ma20 = _safe_float(latest.get("ma20"))
    rsi14 = _safe_float(latest.get("rsi14"))
    macd = _safe_float(latest.get("macd"))
    signal_line = _safe_float(latest.get("signal_line"))
    close_price = _safe_float(latest.get("close_price"))

    score = 0.0
    reasons: list[str] = []
    action = "hold"
    trend_bias = "neutral"
    signal_type = "range"

    if ma5 is not None and ma20 is not None:
        if ma5 > ma20:
            score += 35
            trend_bias = "bullish"
            signal_type = "trend_follow"
            reasons.append("MA5 位于 MA20 上方，短线趋势偏强。")
        elif ma5 < ma20:
            score -= 35
            trend_bias = "bearish"
            signal_type = "trend_follow"
            reasons.append("MA5 位于 MA20 下方，短线趋势偏弱。")

    if rsi14 is not None:
        if rsi14 < 35:
            score += 20
            reasons.append("RSI14 处于低位，存在超跌反弹观察价值。")
        elif rsi14 > 70:
            score -= 25
            reasons.append("RSI14 偏高，短线有过热风险。")
        else:
            reasons.append("RSI14 位于中性区间。")

    if macd is not None and signal_line is not None:
        if macd > signal_line:
            score += 15
            reasons.append("MACD 位于信号线上方，动量略偏多。")
        elif macd < signal_line:
            score -= 15
            reasons.append("MACD 位于信号线下方，动量略偏空。")

    if score >= 30:
        action = "buy_watch"
    elif score <= -30:
        action = "sell_watch"

    explanation = f"最新收盘价约 {close_price:.2f}。" if close_price is not None else "暂无最新收盘价。"
    if reasons:
        explanation = f"{explanation}{''.join(reasons)}"

    return {
        "signal_type": signal_type,
        "score": round(score, 2),
        "action": action,
        "trend_bias": trend_bias,
        "explanation": explanation,
    }


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
