"""
Pre-Flight Diagnostic Suite for India Trader.
Verifies all operational subsystems before 9:00 AM market open.
"""

import sys
import json
import base64
from datetime import datetime, timezone, timedelta
from core.config import config
from core.database import db
from core.upstox_client import client
from core.indicators import compute_position_size

def run_preflight_check() -> bool:
    print("=" * 65)
    print("🔍 INDIA TRADER PRE-FLIGHT SYSTEM DIAGNOSTICS")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 65)

    all_passed = True

    # 1. Token & Expiration Check
    print("\n[1/5] Checking Upstox API Credentials...")
    if not config.access_token:
        print("  ❌ FAIL: UPSTOX_ACCESS_TOKEN is missing from .env")
        all_passed = False
    else:
        try:
            parts = config.access_token.split(".")
            if len(parts) >= 2:
                payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
                payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))
                exp = payload.get("exp")
                if exp:
                    exp_dt = datetime.fromtimestamp(exp, tz=timezone(timedelta(hours=5, minutes=30)))
                    print(f"  ✅ Token format valid. Extended expiry: {exp_dt.strftime('%Y-%m-%d %H:%M:%S IST')}")
                else:
                    print("  ✅ Token present (no exp claim found).")
        except Exception as e:
            print(f"  ⚠️ Warning: Could not decode token claims: {e}")

    # 2. Upstox API Connectivity & Exchange Status
    print("\n[2/5] Testing Upstox API v2 Live Connectivity...")
    try:
        status_res = client.get_market_status("NSE")
        nse_state = status_res.get("data", {}).get("status", "UNKNOWN")
        print(f"  ✅ Connected successfully. NSE Exchange Status: '{nse_state}'")
    except Exception as e:
        print(f"  ❌ FAIL: Cannot connect to Upstox API: {e}")
        all_passed = False

    # 3. Database & Compounding Ledger Health
    print(f"\n[3/5] Verifying SQLite Database & Ledger (₹{config.initial_capital:,.2f} Baseline)...")
    try:
        acct = db.get_account()
        open_trades = db.get_open_trades()
        print(f"  ✅ Database active at data/india_trader.db")
        print(f"     • Capital Balance: ₹{acct['current_capital']:,.2f}")
        print(f"     • Win/Loss Record: {acct['win_count']}W / {acct['loss_count']}L")
        print(f"     • Open Trades    : {len(open_trades)} active")
    except Exception as e:
        print(f"  ❌ FAIL: Database error: {e}")
        all_passed = False

    # 4. Watchlist Quote Feed Resolution
    print("\n[4/5] Testing Live Quotes for 8 Liquid NSE Instruments...")
    try:
        keys = [inst.instrument_key for inst in config.instruments.values()]
        quotes = client.get_market_quotes(keys)
        resolved_count = 0
        for sym, inst in config.instruments.items():
            q = quotes.get(f"NSE_EQ:{sym}")
            if q and q.get("last_price"):
                resolved_count += 1
            else:
                print(f"     ⚠️ Quote missing for {sym} ({inst.instrument_key})")
        print(f"  ✅ {resolved_count}/{len(config.instruments)} instruments resolved with live LTP feeds.")
        if resolved_count < len(config.instruments):
            all_passed = False
    except Exception as e:
        print(f"  ❌ FAIL: Failed to fetch watchlist quotes: {e}")
        all_passed = False

    # 5. Risk Management & Position Sizing Calculator
    print(f"\n[5/5] Testing Position Sizing Engine (₹{config.initial_capital:,.2f} Baseline)...")
    try:
        sample = compute_position_size(
            current_capital=config.initial_capital,
            entry_price=190.24,
            stop_loss=186.00,
            target_price=199.00,
            max_risk_pct=config.max_risk_pct,
            max_allocation_pct=config.max_allocation_pct
        )
        max_allowed_risk = round(config.initial_capital * (config.max_risk_pct / 100.0), 2)
        max_allowed_alloc = round(config.initial_capital * (config.max_allocation_pct / 100.0), 2)
        assert sample["total_risk_inr"] <= max_allowed_risk, f"Risk exceeded ₹{max_allowed_risk}: {sample['total_risk_inr']}"
        assert sample["capital_deployed"] <= max_allowed_alloc, f"Allocation exceeded ₹{max_allowed_alloc}: {sample['capital_deployed']}"
        print(f"  ✅ Position sizing engine verified:")
        print(f"     • Max Risk Cap    : ₹{max_allowed_risk:.2f} | Actual: ₹{sample['total_risk_inr']:.2f}")
        print(f"     • Max Alloc Cap   : ₹{max_allowed_alloc:.2f} | Actual: ₹{sample['capital_deployed']:.2f}")
        print(f"     • Recommended Qty : {sample['quantity']} shares (1:{sample['risk_reward_ratio']} R:R)")
    except Exception as e:
        print(f"  ❌ FAIL: Sizing calculator failed: {e}")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print("🟢 ALL PRE-FLIGHT CHECKS PASSED. SYSTEM READY FOR 9:00 AM IST.")
    else:
        print("🔴 DIAGNOSTIC WARNING: Some subsystems reported issues. Check above.")
    print("=" * 65 + "\n")
    return all_passed

if __name__ == "__main__":
    success = run_preflight_check()
    sys.exit(0 if success else 1)
