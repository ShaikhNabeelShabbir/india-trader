import os
import sqlite3
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from core.config import config

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'india_trader.db')

def get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
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
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            exchange TEXT NOT NULL DEFAULT 'NSE',
            side TEXT NOT NULL DEFAULT 'BUY',
            qty INTEGER NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL,
            stop_loss REAL NOT NULL,
            initial_stop_loss REAL NOT NULL,
            target_price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'OPEN',
            strategy TEXT NOT NULL,
            rationale TEXT,
            realized_pnl REAL DEFAULT 0.0,
            pnl_pct REAL DEFAULT 0.0,
            entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            exited_at TIMESTAMP
        );
        """)

        conn.execute("""
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
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT NOT NULL,
            symbol TEXT,
            message TEXT NOT NULL
        );
        """)

        # Seed initial account if empty
        cur = conn.execute("SELECT COUNT(*) FROM account")
        if cur.fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO account (initial_capital, current_capital, peak_capital) VALUES (?, ?, ?)",
                (config.initial_capital, config.initial_capital, config.initial_capital)
            )
    conn.close()

class DatabaseManager:
    def __init__(self):
        init_db()

    def get_account(self) -> Dict[str, Any]:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM account ORDER BY id DESC LIMIT 1").fetchone()
            if row:
                return dict(row)
            return {
                "initial_capital": config.initial_capital,
                "current_capital": config.initial_capital,
                "peak_capital": config.initial_capital,
                "total_realized_pnl": 0.0,
                "win_count": 0,
                "loss_count": 0,
            }

    def record_trade(
        self,
        symbol: str,
        side: str,
        qty: int,
        entry_price: float,
        stop_loss: float,
        target_price: float,
        strategy: str,
        rationale: str = ""
    ) -> int:
        with get_connection() as conn:
            cur = conn.execute("""
                INSERT INTO trades (symbol, exchange, side, qty, entry_price, stop_loss, initial_stop_loss, target_price, status, strategy, rationale)
                VALUES (?, 'NSE', ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?)
            """, (symbol.upper(), side.upper(), qty, entry_price, stop_loss, stop_loss, target_price, strategy, rationale))
            return cur.lastrowid

    def get_open_trades(self) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM trades WHERE status = 'OPEN' ORDER BY entered_at DESC").fetchall()
            return [dict(r) for r in rows]

    def update_stop_loss(self, trade_id: int, new_stop_loss: float) -> bool:
        with get_connection() as conn:
            conn.execute("UPDATE trades SET stop_loss = ? WHERE id = ?", (new_stop_loss, trade_id))
            return True

    def update_target_price(self, trade_id: int, new_target: float) -> bool:
        with get_connection() as conn:
            conn.execute("UPDATE trades SET target_price = ? WHERE id = ?", (new_target, trade_id))
            return True

    def close_trade(self, trade_id: int, exit_price: float) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM trades WHERE id = ? AND status = 'OPEN'", (trade_id,)).fetchone()
            if not row:
                return None
            trade = dict(row)
            side = trade['side']
            qty = trade['qty']
            entry = trade['entry_price']

            if side == 'BUY':
                pnl = (exit_price - entry) * qty
                pnl_pct = ((exit_price - entry) / entry) * 100.0
            else:
                pnl = (entry - exit_price) * qty
                pnl_pct = ((entry - exit_price) / entry) * 100.0

            conn.execute("""
                UPDATE trades
                SET exit_price = ?, status = 'CLOSED', realized_pnl = ?, pnl_pct = ?, exited_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (exit_price, round(pnl, 2), round(pnl_pct, 2), trade_id))

            # Update account
            acct = self.get_account()
            new_capital = round(acct['current_capital'] + pnl, 2)
            peak = max(acct['peak_capital'], new_capital)
            total_pnl = round(acct['total_realized_pnl'] + pnl, 2)
            wins = acct['win_count'] + (1 if pnl > 0 else 0)
            losses = acct['loss_count'] + (1 if pnl < 0 else 0)

            conn.execute("""
                UPDATE account
                SET current_capital = ?, peak_capital = ?, total_realized_pnl = ?, win_count = ?, loss_count = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_capital, peak, total_pnl, wins, losses, acct['id']))

            trade['exit_price'] = exit_price
            trade['realized_pnl'] = pnl
            trade['pnl_pct'] = pnl_pct
            return trade

    def add_note(self, category: str, message: str, symbol: Optional[str] = None):
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO notes (category, symbol, message) VALUES (?, ?, ?)",
                (category, symbol, message)
            )

db = DatabaseManager()
