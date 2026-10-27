"""
India Trader - Real-Time Market Data WebSocket Streamer (Upstox API v3).
Provides push-based live tick streaming, in-memory price caching, and real-time triggers.
"""

import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Callable, Optional, Any
import upstox_client
from core.config import config

class MarketStreamer:
    def __init__(self, instrument_keys: Optional[List[str]] = None, mode: str = "ltpc"):
        self.mode = mode
        self.instrument_keys = instrument_keys or [inst.instrument_key for inst in config.instruments.values()]
        
        # Configure Upstox API client
        self.configuration = upstox_client.Configuration()
        self.configuration.access_token = config.access_token
        self.api_client = upstox_client.ApiClient(self.configuration)
        
        self.streamer: Optional[upstox_client.MarketDataStreamerV3] = None
        self._thread: Optional[threading.Thread] = None
        self._is_running = False
        
        # In-memory real-time price cache
        # {instrument_key: {"ltp": float, "cp": float, "chg": float, "pct": float, "ts": datetime}}
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        # Registered alert listeners: list of dicts with (symbol, target, condition, callback)
        self.alerts: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def _setup_streamer(self):
        self.streamer = upstox_client.MarketDataStreamerV3(
            api_client=self.api_client,
            instrumentKeys=self.instrument_keys,
            mode=self.mode
        )
        self.streamer.on('open', self._on_open)
        self.streamer.on('message', self._on_message)
        self.streamer.on('error', self._on_error)
        self.streamer.on('close', self._on_close)

    def _on_open(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🟢 WebSocket Streamer Connected (Monitoring {len(self.instrument_keys)} instruments)")

    def _on_message(self, data: Any):
        try:
            # Handle dictionary payload
            if isinstance(data, str):
                data = json.loads(data)
                
            feeds = data.get("feeds", {})
            for key, val in feeds.items():
                ltpc = val.get("ltpc", {})
                if not ltpc:
                    # In 'full' mode, feeds might be structured differently
                    full_feed = val.get("fullFeed", {})
                    market_ff = full_feed.get("marketFF", {})
                    ltpc = market_ff.get("ltpc", {})
                
                ltp = float(ltpc.get("ltp", 0.0))
                cp = float(ltpc.get("cp", 0.0))
                if ltp > 0:
                    chg = round(ltp - cp, 2) if cp > 0 else 0.0
                    pct = round((chg / cp) * 100, 2) if cp > 0 else 0.0
                    
                    with self._lock:
                        self.cache[key] = {
                            "ltp": ltp,
                            "cp": cp,
                            "chg": chg,
                            "pct": pct,
                            "updated_at": datetime.now()
                        }
                    
                    # Check registered alerts
                    self._check_alerts(key, ltp)
        except Exception as e:
            # Silently handle unparseable frames
            pass

    def _check_alerts(self, instrument_key: str, current_price: float):
        # Resolve symbol from instrument_key
        symbol = None
        for sym, inst in config.instruments.items():
            if inst.instrument_key == instrument_key:
                symbol = sym
                break
        
        if not symbol:
            return

        with self._lock:
            remaining_alerts = []
            for alert in self.alerts:
                if alert["symbol"] == symbol:
                    target = alert["target"]
                    cond = alert["condition"]
                    triggered = False
                    
                    if cond == ">=" and current_price >= target:
                        triggered = True
                    elif cond == "<=" and current_price <= target:
                        triggered = True
                    
                    if triggered:
                        try:
                            alert["callback"](symbol, current_price, target)
                        except Exception as ex:
                            print(f"Error in alert callback: {ex}")
                    else:
                        remaining_alerts.append(alert)
                else:
                    remaining_alerts.append(alert)
            self.alerts = remaining_alerts

    def _on_error(self, error):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ WebSocket Error: {error}")

    def _on_close(self, code, reason):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔌 WebSocket Connection Closed: {code} - {reason}")
        self._is_running = False

    def start(self, daemon: bool = True):
        """Starts the WebSocket stream in a background thread."""
        if self._is_running:
            return
        self._is_running = True
        self._setup_streamer()
        self._thread = threading.Thread(target=self.streamer.connect)
        self._thread.daemon = daemon
        self._thread.start()

    def stop(self):
        """Disconnects the WebSocket stream."""
        if self.streamer:
            self.streamer.disconnect()
        self._is_running = False

    def get_price(self, symbol: str) -> Optional[float]:
        """Get instant latest price for a symbol from in-memory cache."""
        inst = config.instruments.get(symbol)
        if not inst:
            return None
        with self._lock:
            data = self.cache.get(inst.instrument_key)
            return data["ltp"] if data else None

    def add_alert(self, symbol: str, target_price: float, condition: str, callback: Callable[[str, float, float], None]):
        """Register a real-time price trigger callback."""
        with self._lock:
            self.alerts.append({
                "symbol": symbol,
                "target": target_price,
                "condition": condition,
                "callback": callback
            })

# Global singleton streamer instance
streamer = MarketStreamer()
