from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.config import config
from core.database import db
from core.upstox_client import client
from core.indicators import (
    calculate_ema, calculate_rsi, calculate_atr, compute_position_size,
    calculate_mansfield_rs, calculate_vcp_compression
)

class MarketScanner:
    def __init__(self):
        self.client = client
        self.db = db

    def scan_watchlist(self) -> Dict[str, Any]:
        """
        Scan all liquid NSE watchlist stocks against:
        1. Daily 20 EMA trend filter
        2. Daily RSI momentum filter
        3. Dynamic ATR-based Stop Loss & Target (1:2.0 minimum R:R)
        4. Strict ₹2,000 capital position sizing (1.5% max risk / 80% allocation)
        """
        acct = self.db.get_account()
        current_capital = acct["current_capital"]

        # 1. Fetch live quotes for watchlist and indices
        inst_keys = [inst.instrument_key for inst in config.instruments.values()]
        index_keys = list(config.indices.values())
        sector_keys = list(config.sector_indices.values())
        all_keys = inst_keys + index_keys + sector_keys

        quotes = self.client.get_market_quotes(all_keys)

        # Parse index status
        nifty_quote = quotes.get("NSE_INDEX:Nifty 50", {})
        banknifty_quote = quotes.get("NSE_INDEX:Nifty Bank", {})

        nifty_close = nifty_quote.get("last_price", 0.0)
        nifty_change = nifty_quote.get("net_change", 0.0)

        # Parse sector performance
        sectors_perf = {}
        for sec_name, sec_ik in config.sector_indices.items():
            key = sec_ik.replace("|", ":")
            sq = quotes.get(key, {})
            s_ltp = sq.get("last_price", 0.0)
            s_chg = sq.get("net_change", 0.0)
            s_pct = round((s_chg / (s_ltp - s_chg) * 100), 2) if (s_ltp - s_chg) > 0 else 0.0
            sectors_perf[sec_name] = {
                "ltp": s_ltp,
                "change": s_chg,
                "pct": s_pct,
                "is_green": s_chg > 0
            }

        # 2. Date range for historical candles (last 60 days)
        today = datetime.now()
        to_date = today.strftime("%Y-%m-%d")
        from_date = (today - timedelta(days=60)).strftime("%Y-%m-%d")

        # Fetch Nifty 50 historical candles for Mansfield RS
        nifty_candles_raw = self.client.get_historical_candles(
            config.indices["NIFTY50"], interval="day", to_date=to_date, from_date=from_date
        )
        nifty_closes = [float(c[4]) for c in reversed(nifty_candles_raw)] if nifty_candles_raw else []

        candidates = []
        rejected = []

        for symbol, inst in config.instruments.items():
            quote_key = f"NSE_EQ:{symbol}"
            quote = quotes.get(quote_key, {})
            ltp = quote.get("last_price")
            ohlc = quote.get("ohlc", {})
            prev_close = ohlc.get("close", ltp)

            if not ltp or ltp <= 0:
                continue

            # Fetch daily candles
            try:
                raw_candles = self.client.get_historical_candles(
                    inst.instrument_key,
                    interval="day",
                    to_date=to_date,
                    from_date=from_date
                )
            except Exception as e:
                rejected.append({
                    "symbol": symbol,
                    "reason": f"Failed to fetch candles: {str(e)}",
                    "ltp": ltp
                })
                continue

            if len(raw_candles) < 20:
                rejected.append({
                    "symbol": symbol,
                    "reason": "Insufficient candle history (< 20 days)",
                    "ltp": ltp
                })
                continue

            # Upstox returns newest first: [ [t, o, h, l, c, v], ... ]
            # Reverse to oldest-to-newest for indicator calculation
            candles_asc = list(reversed(raw_candles))
            close_prices = [float(c[4]) for c in candles_asc]

            ema20_series = calculate_ema(close_prices, period=20)
            daily_ema20 = round(ema20_series[-1], 2)
            daily_rsi = calculate_rsi(close_prices, period=14)
            atr14 = calculate_atr(candles_asc, period=14)

            # Trend Filter: Price > Daily 20 EMA and RSI > 50
            is_uptrend = ltp >= daily_ema20
            rsi_bullish = daily_rsi >= 48.0  # Allow mild pullback zone

            if not is_uptrend or not rsi_bullish:
                rejected.append({
                    "symbol": symbol,
                    "name": inst.name,
                    "ltp": ltp,
                    "daily_ema20": daily_ema20,
                    "rsi": daily_rsi,
                    "reason": f"Downtrend/Weak (LTP ₹{ltp} vs 20EMA ₹{daily_ema20}, RSI {daily_rsi})"
                })
                continue

            # Setup generation: 30-Min Pullback / Dip Buy toward EMA
            # Risk = 1.0 * ATR14 (or min ₹1.50)
            # Reward = 2.2 * Risk
            risk_unit = max(round(atr14 * 0.8, 2), round(ltp * 0.012, 2))
            entry_price = round(ltp, 2)
            stop_loss = round(entry_price - risk_unit, 2)
            target_price = round(entry_price + (risk_unit * 2.2), 2)

            sizing = compute_position_size(
                current_capital=current_capital,
                entry_price=entry_price,
                stop_loss=stop_loss,
                target_price=target_price,
                max_risk_pct=config.max_risk_pct,
                max_allocation_pct=config.max_allocation_pct
            )

            # Check if capital requirement fits in ₹1,600 allocation limit
            if sizing["capital_deployed"] > (current_capital * 0.80):
                rejected.append({
                    "symbol": symbol,
                    "reason": f"Capital requirement (₹{sizing['capital_deployed']}) exceeds 80% allocation limit",
                    "ltp": ltp
                })
                continue

            sec_info = sectors_perf.get(inst.sector, {})
            sec_boost = 15.0 if sec_info.get("is_green") else (-10.0 if sec_info.get("pct", 0) < -1.5 else 0.0)

            # Smart Money Indicators: Mansfield Relative Strength & VCP Compression
            m_rs = calculate_mansfield_rs(close_prices, nifty_closes)
            vcp_data = calculate_vcp_compression(candles_asc)
            vcp_boost = 10.0 if vcp_data.get("is_coiled") else 0.0
            rs_boost = 10.0 if m_rs > 0 else -10.0

            candidates.append({
                "symbol": symbol,
                "name": inst.name,
                "sector": inst.sector,
                "sector_pct": sec_info.get("pct", 0.0),
                "sector_green": sec_info.get("is_green", False),
                "mansfield_rs": m_rs,
                "vcp_ratio": vcp_data.get("compression_ratio"),
                "is_coiled": vcp_data.get("is_coiled"),
                "ltp": ltp,
                "daily_ema20": daily_ema20,
                "rsi": daily_rsi,
                "atr14": atr14,
                "strategy": "Daily 20 EMA Pullback Bounce",
                "sizing": sizing,
                "score": round(daily_rsi + ((ltp - daily_ema20) / daily_ema20 * 100) + sec_boost + vcp_boost + rs_boost, 2)
            })

        # Rank candidates by strength score
        candidates.sort(key=lambda x: x["score"], reverse=True)

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
            "capital": current_capital,
            "market_cues": {
                "nifty_close": nifty_close,
                "nifty_change": nifty_change,
                "sentiment": "BULLISH" if nifty_change >= 0 else "BEARISH/DEFENSIVE"
            },
            "sectors": sectors_perf,
            "candidates": candidates,
            "rejected": rejected
        }

scanner = MarketScanner()
