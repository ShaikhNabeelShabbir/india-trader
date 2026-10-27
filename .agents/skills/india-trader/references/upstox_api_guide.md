# Upstox API v2 Technical Guide & Reference

This reference covers the Upstox API v2 architecture, authentication flow, market data endpoints, and read-only security practices for Indian stock market analysis (NSE/BSE).

---

## 1. Upstox API v2 Overview

- **Base URL**: `https://api.upstox.com/v2`
- **Supported Exchanges**: NSE (National Stock Exchange), BSE (Bombay Stock Exchange), MCX
- **Key Principle**: **Read-Only / Market Analytics Access**. The agent analyzes data and generates trade signals, but does **not** execute real-money orders. All transaction execution is manually performed by the user in their Upstox app.

---

## 2. Authentication Flow (OAuth 2.0)

Upstox uses OAuth 2.0. Access tokens are valid for 24 hours (until the next morning before market open).

### Step 1: Create an App on Upstox Developer Portal
1. Go to [developer.upstox.com](https://developer.upstox.com/) and log in with your Upstox credentials.
2. Click **Create New App**.
3. Name: `India Trader Agent`.
4. Redirect URL: `http://127.0.0.1:5000/callback` (or any valid local URL).
5. Copy your **API Key** (`client_id`) and **API Secret** (`client_secret`).

### Step 2: Generate Authorization Code
Visit this URL in your browser:
```text
https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={API_KEY}&redirect_uri={REDIRECT_URI}
```
Log in and approve. The browser redirects to:
`http://127.0.0.1:5000/callback?code={AUTH_CODE}`
Copy the `{AUTH_CODE}` from the URL.

### Step 3: Exchange Code for Access Token
Send a `POST` request to:
```http
POST https://api.upstox.com/v2/login/authorization/token
Content-Type: application/x-www-form-urlencoded
Accept: application/json

code={AUTH_CODE}&client_id={API_KEY}&client_secret={API_SECRET}&redirect_uri={REDIRECT_URI}&grant_type=authorization_code
```
Response JSON:
```json
{
  "email": "user@example.com",
  "user_id": "123456",
  "access_token": "eyJraWQi...",
  "status": "success"
}
```
Store `access_token` in your `.env` file as `UPSTOX_ACCESS_TOKEN`.

---

## 3. Core Market Data Endpoints

All requests require the header:
```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}
```

### A. Full Market Quote (LTP, Depth, OHLC, Volume)
```http
GET https://api.upstox.com/v2/market-quote/quotes?instrument_key=NSE_EQ|INE081A01012
```
*Note*: `instrument_key` format is `{EXCHANGE}|{ISIN_OR_SYMBOL}` (e.g. `NSE_EQ|INE081A01012` for Tata Steel or `NSE_EQ|TATASTEEL`).

Returns:
- `last_price`: Current trading price
- `ohlc`: Open, High, Low, Close
- `volume`: Total traded volume
- `depth`: Top 5 buy/sell bids and asks

### B. Historical Candle Bars (Technical Indicators & Charting)
```http
GET https://api.upstox.com/v2/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}
```
- `interval`: `1minute`, `30minute`, `day`, `week`, `month`
- `to_date`: `YYYY-MM-DD`
- `from_date`: `YYYY-MM-DD`

Candle format returned:
```json
{
  "status": "success",
  "data": {
    "candles": [
      ["2026-10-20T15:30:00+05:30", 156.20, 157.10, 155.80, 156.50, 4820100, 0]
    ]
  }
}
```
Array index mapping:
- `0`: Timestamp (ISO 8601 with +05:30 IST)
- `1`: Open
- `2`: High
- `3`: Low
- `4`: Close
- `5`: Volume
- `6`: Open Interest

### C. Market Status
```http
GET https://api.upstox.com/v2/market/status/NSE
```
Returns exchange state: `NORMAL_OPEN`, `PRE_OPEN`, `CLOSED`, or `POST_CLOSE`.

---

## 4. Upstox Python Client Blueprint (`upstox_client.py`)

```python
import requests
import pandas as pd
from typing import Dict, Any, Optional

class UpstoxClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.upstox.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    def get_market_quote(self, instrument_key: str) -> Dict[str, Any]:
        url = f"{self.base_url}/market-quote/quotes"
        params = {"instrument_key": instrument_key}
        res = requests.get(url, headers=self.headers, params=params, timeout=10)
        res.raise_for_status()
        return res.json()

    def get_historical_candles(self, instrument_key: str, interval: str = "30minute",
                               to_date: str = "", from_date: str = "") -> pd.DataFrame:
        url = f"{self.base_url}/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"
        res = requests.get(url, headers=self.headers, timeout=10)
        res.raise_for_status()
        data = res.json().get("data", {}).get("candles", [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "oi"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
```
