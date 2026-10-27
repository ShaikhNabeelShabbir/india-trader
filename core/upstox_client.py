"""
Upstox API v2 Read-Only Connector.
Architectural Safety Shield:
- STRICTLY READ-ONLY: Only reads market quotes, index states, and historical candles.
- NEVER contains order placement, cancellation, or modification logic.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional
from core.config import config

class UpstoxReadOnlyClient:
    BASE_URL = "https://api.upstox.com/v2"

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or config.access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 IndiaTrader/1.0"
        }

    def _get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        if params:
            qs = urllib.parse.urlencode(params)
            url = f"{url}?{qs}"

        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
                raise RuntimeError(f"Upstox API Error [{e.code}]: {err_json.get('errors') or err_json.get('message') or err_body}")
            except Exception:
                raise RuntimeError(f"Upstox HTTP Error [{e.code}]: {err_body}")
        except Exception as e:
            raise RuntimeError(f"Upstox Connection Error: {str(e)}")

    def get_market_status(self, exchange: str = "NSE") -> Dict[str, Any]:
        """Fetch current exchange operational status (OPEN, CLOSED, PRE_OPEN, etc.)."""
        return self._get(f"/market/status/{exchange}")

    def get_market_quotes(self, instrument_keys: List[str]) -> Dict[str, Any]:
        """Fetch full LTP, OHLC, depth, and volume quotes for instruments."""
        if not instrument_keys:
            return {}
        ik_param = ",".join(instrument_keys)
        res = self._get("/market-quote/quotes", {"instrument_key": ik_param})
        return res.get("data", {})

    def get_historical_candles(
        self,
        instrument_key: str,
        interval: str = "day",
        to_date: str = "",
        from_date: str = ""
    ) -> List[List[Any]]:
        """
        Fetch historical candle bars.
        interval: '1minute', '30minute', 'day', 'week', 'month'
        Returns list of [timestamp, open, high, low, close, volume, oi]
        """
        encoded_key = urllib.parse.quote(instrument_key)
        endpoint = f"/historical-candle/{encoded_key}/{interval}/{to_date}/{from_date}"
        res = self._get(endpoint)
        return res.get("data", {}).get("candles", [])

    def get_intraday_candles(
        self,
        instrument_key: str,
        interval: str = "30minute"
    ) -> List[List[Any]]:
        """Fetch intraday candle bars for the current trading day."""
        encoded_key = urllib.parse.quote(instrument_key)
        endpoint = f"/historical-candle/intraday/{encoded_key}/{interval}"
        res = self._get(endpoint)
        return res.get("data", {}).get("candles", [])

client = UpstoxReadOnlyClient()
