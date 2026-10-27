"""
India Trader CLI & Autonomous Analysis Engine.
Strictly Read-Only Market Analytics for NSE / BSE with Upstox API v2.
"""

import sys
import argparse
from typing import Optional
from datetime import datetime
from core.config import config
from core.database import db
from core.upstox_client import client
from morning_briefing import generate_morning_briefing
from strategies.scanner import scanner
from core.diagnostics import run_preflight_check
from core.eod_review import run_eod_review
from core.websocket_streamer import MarketStreamer

def run_live_streamer(symbols_str: Optional[str] = None, duration_sec: int = 15):
    """Runs a live WebSocket price ticker stream in the terminal."""
    import time
    
    selected_keys = None
    if symbols_str:
        syms = [s.strip().upper() for s in symbols_str.split(',')]
        selected_keys = [config.instruments[s].instrument_key for s in syms if s in config.instruments]
    
    streamer = MarketStreamer(instrument_keys=selected_keys)
    print("\n" + "=" * 65)
    print("📡 INDIA TRADER | LIVE WEBSOCKET MARKET DATA STREAMER (V3)")
    print(f"Connecting to Upstox WebSocket feed... (Streaming for {duration_sec}s)")
    print("=" * 65)
    
    streamer.start(daemon=True)
    time.sleep(1.5)  # Allow socket to establish
    
    start_time = time.time()
    try:
        while time.time() - start_time < duration_sec:
            # Print current snapshot
            with streamer._lock:
                snapshot = dict(streamer.cache)
            
            if snapshot:
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] Live Ticks: ", end="")
                parts = []
                for k, v in snapshot.items():
                    sym = k.split(':')[-1].split('|')[-1]
                    # Map to friendly symbol
                    for s, inst in config.instruments.items():
                        if inst.instrument_key == k:
                            sym = s
                            break
                    parts.append(f"{sym}: ₹{v['ltp']:,.2f} ({v['pct']:+.2f}%)")
                print(" | ".join(parts), end="", flush=True)
            time.sleep(0.5)
        print("\n\n" + "=" * 65)
        print("✅ Stream test completed successfully.")
        print("=" * 65 + "\n")
    except KeyboardInterrupt:
        print("\nStream interrupted by user.")
    finally:
        streamer.stop()

def show_ledger():
    acct = db.get_account()
    open_trades = db.get_open_trades()

    print("\n" + "=" * 55)
    print(f"🇮🇳 INDIA TRADER | COMPOUNDING LEDGER (₹{acct['initial_capital']:,.2f})")
    print("=" * 55)
    print(f" Initial Baseline Capital : ₹{acct['initial_capital']:,.2f}")
    print(f" Current Available Capital: ₹{acct['current_capital']:,.2f}")
    print(f" Peak Capital Recorded    : ₹{acct['peak_capital']:,.2f}")
    print(f" Total Realized P&L       : ₹{acct['total_realized_pnl']:+,.2f}")
    print(f" Win / Loss Ratio         : {acct['win_count']} Wins / {acct['loss_count']} Losses")
    print("-" * 55)

    if not open_trades:
        print(" Active Positions: None (100% Cash / Ready for 9:00 AM Scan)")
    else:
        print(f" Active Positions ({len(open_trades)}):")
        for t in open_trades:
            print(f" • [ID #{t['id']}] {t['symbol']} | Qty: {t['qty']} | Entry: ₹{t['entry_price']} | SL: ₹{t['stop_loss']} | Target: ₹{t['target_price']}")
    print("=" * 55 + "\n")

def check_profit_shield():
    open_trades = db.get_open_trades()
    if not open_trades:
        print("No open positions to monitor.")
        return

    symbols_map = {t["symbol"]: t for t in open_trades}
    keys = []
    for s in symbols_map.keys():
        if s in config.instruments:
            keys.append(config.instruments[s].instrument_key)

    if not keys:
        print("No matching instrument keys for open trades.")
        return

    quotes = client.get_market_quotes(keys)
    print("\n🛡️ PROFIT SHIELD MONITOR:")
    for t in open_trades:
        s = t["symbol"]
        q = quotes.get(f"NSE_EQ:{s}", {})
        ltp = q.get("last_price")
        if not ltp:
            continue

        entry = t["entry_price"]
        gain_pct = ((ltp - entry) / entry) * 100.0
        print(f"\n• {s}: Entry = ₹{entry:.2f} | LTP = ₹{ltp:.2f} | Unrealized Gain = {gain_pct:+.2f}%")

        if gain_pct >= 1.2 and t["stop_loss"] < entry:
            half_qty = max(1, t["qty"] // 2)
            print(f"  🔔 PROFIT SHIELD & SCALE-OUT TRIGGERED: Stock is up {gain_pct:+.2f}% (>= +1.2%)!")
            print(f"  ACTION 1: Book 50% profit in Upstox by selling {half_qty} shares at market/limit.")
            print(f"  ACTION 2: Move Stop Loss on remaining {t['qty'] - half_qty} shares to BREAK-EVEN (₹{entry:.2f}).")
            db.update_stop_loss(t["id"], entry)
            print(f"  ✅ Database updated: Stop Loss for Trade #{t['id']} moved to ₹{entry:.2f} (Risk-Free).")
        elif gain_pct >= 1.0 and t["stop_loss"] < entry:
            print(f"  🔔 BREAK-EVEN TRIGGERED: Stock is up >= +1.0%!")
            print(f"  ACTION: Move Stop Loss from ₹{t['stop_loss']} to BREAK-EVEN (₹{entry:.2f}) in your Upstox App.")
            db.update_stop_loss(t["id"], entry)
            print(f"  ✅ Database updated: Stop Loss for Trade #{t['id']} moved to ₹{entry:.2f} (Risk-Free).")
        elif t["stop_loss"] >= entry:
            print(f"  ✅ Trade is already risk-free (Stop Loss set to Break-Even at ₹{t['stop_loss']}).")
        else:
            print(f"  ⏳ Holding current Stop Loss at ₹{t['stop_loss']}.")

def main():
    parser = argparse.ArgumentParser(description="India Trader Autonomous Assistant")
    subparsers = parser.add_subparsers(dest="command")

    # Briefing
    subparsers.add_parser("briefing", help="Generate 9:00 AM Pre-Market Action Card")

    # End-of-Day Review
    subparsers.add_parser("review", help="Generate 3:35 PM End-of-Day Performance Debrief & Snapshot")

    # Diagnostic Pre-flight Check
    subparsers.add_parser("check", help="Run full pre-flight system diagnostics")

    # Scan
    subparsers.add_parser("scan", help="Scan watchlist for setups")

    # Ledger
    subparsers.add_parser("ledger", help="Display compounding balance & open trades")

    # Profit Shield
    subparsers.add_parser("profit-shield", help="Check open trades and trigger break-even stop loss")

    # Log Trade
    log_parser = subparsers.add_parser("log-trade", help="Record a trade manually executed in Upstox")
    log_parser.add_argument("--symbol", required=True, help="Stock symbol (e.g. TATASTEEL)")
    log_parser.add_argument("--qty", type=int, required=True, help="Quantity executed")
    log_parser.add_argument("--entry", type=float, required=True, help="Entry price")
    log_parser.add_argument("--sl", type=float, required=True, help="Stop loss price")
    log_parser.add_argument("--target", type=float, required=True, help="Target price")
    log_parser.add_argument("--strategy", default="Pullback Bounce", help="Strategy name")
    log_parser.add_argument("--notes", default="", help="Trade rationale")

    # Close Trade
    close_parser = subparsers.add_parser("close-trade", help="Record exit of an open trade")
    close_parser.add_argument("--id", type=int, required=True, help="Trade ID")
    close_parser.add_argument("--exit", type=float, required=True, help="Exit execution price")

    # WebSocket Streamer
    stream_parser = subparsers.add_parser("stream", help="Stream live market prices via Upstox WebSocket (V3)")
    stream_parser.add_argument("--symbols", type=str, default=None, help="Comma-separated symbols to stream (e.g. SBIN,WIPRO)")
    stream_parser.add_argument("--duration", type=int, default=15, help="Duration in seconds to stream")

    args = parser.parse_args()

    if args.command == "briefing" or not args.command:
        print(generate_morning_briefing())
    elif args.command == "review":
        print(run_eod_review())
    elif args.command == "stream":
        run_live_streamer(symbols_str=args.symbols, duration_sec=args.duration)
    elif args.command == "check":
        run_preflight_check()
    elif args.command == "scan":
        results = scanner.scan_watchlist()
        print(f"\nScanned {len(config.instruments)} stocks. Found {len(results['candidates'])} qualifying candidates.")
        for c in results["candidates"]:
            print(f" • {c['symbol']}: LTP ₹{c['ltp']} | 20EMA ₹{c['daily_ema20']} | RSI {c['rsi']} | Score: {c['score']}")
    elif args.command == "ledger":
        show_ledger()
    elif args.command == "profit-shield":
        check_profit_shield()
    elif args.command == "log-trade":
        tid = db.record_trade(
            symbol=args.symbol,
            side="BUY",
            qty=args.qty,
            entry_price=args.entry,
            stop_loss=args.sl,
            target_price=args.target,
            strategy=args.strategy,
            rationale=args.notes
        )
        print(f"✅ Trade #{tid} successfully recorded in ledger: Bought {args.qty} {args.symbol.upper()} at ₹{args.entry:.2f}")
    elif args.command == "close-trade":
        trade = db.close_trade(args.id, args.exit)
        if trade:
            print(f"✅ Trade #{trade['id']} closed at ₹{args.exit:.2f}. Realized P&L: ₹{trade['realized_pnl']:+,.2f} ({trade['pnl_pct']:+,.2f}%)")
            show_ledger()
        else:
            print(f"❌ Error: Open trade with ID #{args.id} not found.")

if __name__ == "__main__":
    main()
