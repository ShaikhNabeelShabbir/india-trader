"""
9:00 AM IST Pre-Market Action Plan Generator.
Runs institutional scans and prepares exact position sizes for the ₹2,000 baseline.
"""

from datetime import datetime
from core.database import db
from core.upstox_client import client
from strategies.scanner import scanner

def generate_morning_briefing() -> str:
    # 1. Market Status
    try:
        status_res = client.get_market_status("NSE")
        mkt_status = status_res.get("data", {}).get("status", "UNKNOWN")
    except Exception as e:
        mkt_status = f"Unavailable ({str(e)})"

    # 2. Run Scanner
    results = scanner.scan_watchlist()
    acct = db.get_account()

    capital = acct['current_capital']
    risk_budget = round(capital * 0.015, 2)
    reserve_cash = round(capital * 0.20, 2)

    lines = []
    lines.append("=" * 65)
    lines.append(f"🇮🇳 INDIA TRADER | PRE-MARKET ACTION CARD (NSE/BSE)")
    lines.append(f"Generated: {results['timestamp']} | NSE State: {mkt_status}")
    lines.append(f"Capital: ₹{capital:,.2f} | Max Risk (1.5%): ₹{risk_budget:,.2f} | Cash Reserve: ₹{reserve_cash:,.2f}")
    lines.append("=" * 65)

    mc = results["market_cues"]
    lines.append(f"\n📊 Benchmark Sentiment: NIFTY 50 @ {mc['nifty_close']} ({mc['nifty_change']:+.2f}) -> [{mc['sentiment']}]")
    
    # Display Sector Leaderboard
    sec_data = results.get("sectors", {})
    if sec_data:
        sorted_sec = sorted(sec_data.items(), key=lambda x: x[1]["pct"], reverse=True)
        sec_strs = [f"{k}: {v['pct']:+.2f}%" for k, v in sorted_sec]
        lines.append(f"🏆 Sector Heatmap: {' | '.join(sec_strs)}")
    lines.append("-" * 65)

    candidates = results["candidates"]
    if not candidates:
        lines.append("\n⚠️ NO HIGH-PROBABILITY SETUPS FOUND TODAY.")
        lines.append("Rule: 'No edge, no trade.' Capital preservation is priority #1.")
        if results["rejected"]:
            lines.append("\nWatchlist Filter Notes:")
            for r in results["rejected"][:4]:
                lines.append(f" • {r['symbol']}: {r.get('reason', 'Failed technical filters')}")
    else:
        lines.append(f"\n🎯 QUALIFYING SETUPS ({len(candidates)} Found) — STRICT READ-ONLY RECOMMENDATION:")
        for idx, cand in enumerate(candidates[:2], 1):
            s = cand["sizing"]
            lines.append(f"\n[{idx}] {cand['symbol']} ({cand['name']}) — Sector: {cand['sector']}")
            lines.append(f"    • Strategy      : {cand['strategy']}")
            lines.append(f"    • Institutional : Mansfield RS: {cand.get('mansfield_rs', 0):+4.1f}% vs Nifty | VCP Compression: {cand.get('vcp_ratio', 1.0)}x")
            lines.append(f"    • Daily Context : 20 EMA = ₹{cand['daily_ema20']} | RSI(14) = {cand['rsi']}")
            lines.append(f"    • Action Plan   : BUY LIMIT")
            lines.append(f"    • Entry Price   : ₹{s['entry_price']:.2f}")
            lines.append(f"    • Stop Loss     : ₹{s['stop_loss']:.2f} (Risk: ₹{s['risk_per_share']:.2f} / share)")
            lines.append(f"    • Profit Target : ₹{s['target_price']:.2f} (Reward: ₹{s['reward_per_share']:.2f} / share)")
            lines.append(f"    • Risk / Reward : 1:{s['risk_reward_ratio']} R:R")
            lines.append(f"    • Order Qty     : {s['quantity']} shares")
            lines.append(f"    • Capital Used  : ₹{s['capital_deployed']:.2f} (Risk: ₹{s['total_risk_inr']:.2f} / {s['risk_pct_of_capital']}%)")
            lines.append(f"    • Max Potential : +₹{s['potential_reward_inr']:.2f} (+{s['reward_pct_of_capital']}%)")

    lines.append("\n" + "=" * 65)
    lines.append("🛡️ EXECUTION & SAFETY PROTOCOL:")
    lines.append(" 1. The agent is strictly READ-ONLY and will NEVER place trades automatically.")
    lines.append(" 2. Enter orders manually in your Upstox App at 9:15 AM opening bell.")
    lines.append(" 3. When stock moves +1.0% in profit, move Stop Loss to Break-Even immediately.")
    lines.append(" 4. Report fills back to the agent: 'Bought [QTY] [SYMBOL] at [PRICE]'.")
    lines.append("=" * 65)

    briefing_text = "\n".join(lines)

    # Save to notes table
    db.add_note(category="PRE_MARKET", message=briefing_text)
    return briefing_text

if __name__ == "__main__":
    print(generate_morning_briefing())
