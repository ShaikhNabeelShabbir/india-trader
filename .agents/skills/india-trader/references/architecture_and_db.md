# India Trader Architecture & Database Schema

This reference outlines the software architecture, SQLite database schema, and project layout for the independent **India Trader** project.

---

## 1. Project Directory Layout

```text
india-trader/
├── .env                         # UPSTOX_API_KEY, UPSTOX_API_SECRET, UPSTOX_ACCESS_TOKEN
├── .gitignore                   # Ignore .venv, .env, *.db, *.log
├── requirements.txt             # requests, pandas, numpy, python-dotenv
├── main.py                      # Interactive CLI and daily report runner
├── morning_briefing.py          # 9:00 AM IST Pre-Market Briefing Generator
├── core/
│   ├── __init__.py
│   ├── config.py                # Starting capital (₹2,000), watchlist, risk %
│   ├── database.py              # SQLite ledger & compounding manager
│   └── upstox_client.py         # Read-only Upstox API v2 connector
├── strategies/
│   ├── __init__.py
│   ├── base.py                  # Signal dataclass and BaseStrategy
│   ├── momentum_orb.py          # 15-Minute Opening Range Breakout
│   ├── trend_pullback.py        # Daily 20 EMA + 30-Min Pullback
│   └── scanner.py               # NSE Watchlist scanner
├── data/
│   └── india_trader.db          # Persistent SQLite database
└── docs/
    └── runbook.md               # Daily morning operational guide
```

---

## 2. Database Schema (`data/india_trader.db`)

```sql
-- 1. Account Ledger (tracks our ₹2,000 starting bankroll and compounding growth)
CREATE TABLE IF NOT EXISTS account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    initial_capital REAL NOT NULL DEFAULT 2000.0,
    current_capital REAL NOT NULL DEFAULT 2000.0,
    peak_capital REAL NOT NULL DEFAULT 2000.0,
    total_realized_pnl REAL NOT NULL DEFAULT 0.0,
    win_count INTEGER NOT NULL DEFAULT 0,
    loss_count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Trade Log (tracks every trade entered, target, stop loss, and outcome)
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,                  -- e.g. TATASTEEL
    exchange TEXT NOT NULL DEFAULT 'NSE',  -- NSE or BSE
    side TEXT NOT NULL,                    -- BUY or SELL
    qty INTEGER NOT NULL,                  -- Number of shares
    entry_price REAL NOT NULL,             -- Execution price
    exit_price REAL,                       -- Closing price
    stop_loss REAL NOT NULL,               -- Protective stop
    target_price REAL NOT NULL,            -- Profit objective
    status TEXT NOT NULL DEFAULT 'OPEN',   -- OPEN, CLOSED, CANCELLED
    strategy TEXT NOT NULL,                -- e.g. 15m_ORB, Trend_Pullback
    rationale TEXT,                        -- Technical setup explanation
    realized_pnl REAL DEFAULT 0.0,         -- Net profit/loss in INR
    pnl_pct REAL DEFAULT 0.0,              -- Percentage gain/loss
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exited_at TIMESTAMP
);

-- 3. Daily Equity Snapshots (for performance curves and win-rate analysis)
CREATE TABLE IF NOT EXISTS daily_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date DATE UNIQUE NOT NULL,
    starting_equity REAL NOT NULL,
    ending_equity REAL NOT NULL,
    daily_pnl REAL NOT NULL,
    daily_pnl_pct REAL NOT NULL,
    trades_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Trade Notes & Memory (for conversational recall in Antigravity)
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category TEXT NOT NULL,                -- PRE_MARKET, TRADE_DECISION, LESSON
    symbol TEXT,
    message TEXT NOT NULL
);
```

---

## 3. Core Configuration Blueprint (`core/config.py`)

```python
import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Upstox Credentials
    upstox_api_key: str = os.getenv("UPSTOX_API_KEY", "")
    upstox_api_secret: str = os.getenv("UPSTOX_API_SECRET", "")
    upstox_access_token: str = os.getenv("UPSTOX_ACCESS_TOKEN", "")

    # Hardcoded Capital Baseline
    initial_capital_inr: float = 2000.0
    max_risk_pct_per_trade: float = 1.5      # Max 1.5% risk = ₹30 per trade
    max_capital_allocation_pct: float = 80.0 # Max 80% capital = ₹1,600 deployed

    # Default High-Liquidity NSE Momentum Watchlist (Priced under ₹1,500)
    watchlist: List[str] = field(default_factory=lambda: [
        "TATASTEEL", "ZOMATO", "ITC", "SBIN", "TATAMOTORS", "WIPRO", "COALINDIA", "NTPC"
    ])

    database_path: str = os.getenv("DATABASE_PATH", "data/india_trader.db")

config = Config()
```
