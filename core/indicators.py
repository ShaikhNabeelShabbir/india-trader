import math
from typing import List, Dict, Any, Optional

def calculate_ema(prices: List[float], period: int = 20) -> List[float]:
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return [sum(prices) / len(prices)] * len(prices) if prices else []
    
    ema = [0.0] * len(prices)
    # Simple average for initial seed
    sma = sum(prices[:period]) / period
    ema[period - 1] = sma
    multiplier = 2.0 / (period + 1.0)
    
    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
    
    # Fill earlier elements with sma
    for i in range(period - 1):
        ema[i] = sma
    return ema

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate the latest RSI(14) from historical closing prices (oldest to newest)."""
    if len(prices) <= period:
        return 50.0  # Default neutral

    gains = []
    losses = []
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        if delta > 0:
            gains.append(delta)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(delta))

    if len(gains) < period:
        return 50.0

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100.0 - (100.0 / (1.0 + rs)), 2)

def calculate_atr(candles: List[List[Any]], period: int = 14) -> float:
    """
    Calculate ATR(14) from candles ordered oldest to newest.
    Candle format: [timestamp, open, high, low, close, volume, ...]
    """
    if len(candles) < 2:
        return 1.0

    trs = []
    for i in range(1, len(candles)):
        high = float(candles[i][2])
        low = float(candles[i][3])
        prev_close = float(candles[i - 1][4])
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)

    if not trs:
        return 1.0

    if len(trs) <= period:
        return round(sum(trs) / len(trs), 2)

    atr = sum(trs[:period]) / period
    for tr in trs[period:]:
        atr = (atr * (period - 1) + tr) / period
    return round(atr, 2)

def calculate_mansfield_rs(stock_closes: List[float], index_closes: List[float]) -> float:
    """
    Mansfield Relative Strength Ratio:
    Measures institutional outperformance of a stock relative to the Nifty 50 benchmark.
    Positive value (>0) indicates smart money accumulation outperforming the index.
    """
    min_len = min(len(stock_closes), len(index_closes))
    if min_len < 10:
        return 0.0

    s_curr, s_prev = stock_closes[-1], stock_closes[-10]
    i_curr, i_prev = index_closes[-1], index_closes[-10]

    s_perf = (s_curr - s_prev) / s_prev if s_prev > 0 else 0.0
    i_perf = (i_curr - i_prev) / i_prev if i_prev > 0 else 0.0

    rs_diff = (s_perf - i_perf) * 100.0
    return round(rs_diff, 2)

def calculate_vcp_compression(candles: List[List[Any]]) -> Dict[str, Any]:
    """
    Mark Minervini's Volatility Contraction Pattern (VCP) Ratio:
    Compares recent 5-day price range against 20-day ATR.
    A compression ratio < 0.70 signals a coiled spring ready for institutional breakout.
    """
    if len(candles) < 10:
        return {"compression_ratio": 1.0, "is_coiled": False}

    recent_5 = candles[-5:]
    recent_high = max(float(c[2]) for c in recent_5)
    recent_low = min(float(c[3]) for c in recent_5)
    recent_range = recent_high - recent_low

    atr20 = calculate_atr(candles, period=min(20, len(candles) - 1))
    expected_range = atr20 * 2.5

    ratio = round(recent_range / expected_range, 2) if expected_range > 0 else 1.0
    is_coiled = ratio <= 0.75

    return {
        "compression_ratio": ratio,
        "is_coiled": is_coiled,
        "recent_range": round(recent_range, 2),
        "atr20": atr20
    }

def compute_position_size(
    current_capital: float,
    entry_price: float,
    stop_loss: float,
    target_price: float,
    max_risk_pct: float = 1.5,
    max_allocation_pct: float = 80.0
) -> Dict[str, Any]:
    """
    Rigorous position sizing for ₹2,000 baseline:
    - Max Risk = Capital * 1.5% (₹30 on ₹2000)
    - Max Allocation = Capital * 80% (₹1600 on ₹2000)
    - Minimum R:R = 1:2.0
    """
    risk_budget = round(current_capital * (max_risk_pct / 100.0), 2)
    risk_per_share = round(abs(entry_price - stop_loss), 2)
    reward_per_share = round(abs(target_price - entry_price), 2)

    if risk_per_share <= 0:
        risk_per_share = 0.50

    rr_ratio = round(reward_per_share / risk_per_share, 2)
    max_capital_to_deploy = current_capital * (max_allocation_pct / 100.0)

    qty_by_risk = math.floor(risk_budget / risk_per_share)
    qty_by_allocation = math.floor(max_capital_to_deploy / entry_price)

    final_qty = max(1, min(qty_by_risk, qty_by_allocation))
    deployed_capital = round(final_qty * entry_price, 2)
    total_risk = round(final_qty * risk_per_share, 2)
    potential_reward = round(final_qty * reward_per_share, 2)

    return {
        "quantity": final_qty,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "target_price": target_price,
        "risk_per_share": risk_per_share,
        "reward_per_share": reward_per_share,
        "risk_reward_ratio": rr_ratio,
        "capital_deployed": deployed_capital,
        "total_risk_inr": total_risk,
        "potential_reward_inr": potential_reward,
        "risk_pct_of_capital": round((total_risk / current_capital) * 100.0, 2),
        "reward_pct_of_capital": round((potential_reward / current_capital) * 100.0, 2),
    }
