# Indian Equity Strategy Playbook (NSE / BSE)

This playbook outlines the three quantitative trading setups tailored for high-liquidity NSE equities, designed to maximize profit while strictly capping downside risk.

---

## Strategy 1: Pre-Market Gap & 15-Minute Opening Range Breakout (ORB)

### Context & Timing
- **Scan Window**: 9:00 AM – 9:08 AM IST (NSE Pre-Open Auction)
- **Execution Window**: 9:30 AM – 10:15 AM IST (After opening 15-minute candle forms)
- **Best Instruments**: `TATASTEEL`, `ZOMATO`, `TATAMOTORS`, `SBIN`

### Setup Rules
1. **Pre-Market Filter**:
   - Stock gaps up between +0.8% and +2.5% in the 9:00 AM pre-market auction.
   - Overall market sentiment (GIFT Nifty) is green or neutral.
2. **Opening 15-Minute Candle (9:15 – 9:30 AM)**:
   - Allow the first 15-minute candle to close.
   - Note the **15-Min High ($H_{15}$)** and **15-Min Low ($L_{15}$)**.
3. **Entry Trigger**:
   - When the next candle breaks above $H_{15}$ with volume > 1.3x average volume.
   - Price must be trading above the Volume Weighted Average Price (VWAP).
4. **Risk & Target Parameters**:
   - **Entry**: $H_{15} + ₹0.20$
   - **Stop Loss**: $L_{15}$ (or VWAP, whichever is closer)
   - **Target 1**: Entry + $1.0 \times (H_{15} - L_{15})$ (Bank 50% profit)
   - **Target 2**: Entry + $2.0 \times (H_{15} - L_{15})$ (Trail remaining 50%)

---

## Strategy 2: Multi-Timeframe Trend Following (Daily + 30-Min Pullback)

### Context & Timing
- **Scan Window**: 9:00 AM IST (Daily pre-market briefing)
- **Execution Window**: 9:45 AM – 1:30 PM IST (Intraday momentum swings)
- **Best Instruments**: `ITC`, `WIPRO`, `TATAMOTORS`, `SBIN`, `COALINDIA`

### Setup Rules
1. **Daily Macro Filter**:
   - Daily Close > Daily 20-day Exponential Moving Average (EMA).
   - Daily RSI(14) > 52 (Bullish territory).
2. **Intraday Pullback (30-Minute Chart)**:
   - Price pulls back toward the 21-period EMA on the 30-minute chart.
   - 30-minute RSI cools down into the **42–52 support zone**.
   - Price prints a bullish confirmation candle (Close > Open and above 9 EMA).
3. **Risk & Target Parameters**:
   - **Stop Loss**: `Entry - (1.5 * ATR_14)`
   - **Take Profit**: `Entry + (3.0 * ATR_14)`
   - **Risk-to-Reward Ratio**: Minimum 1:2.0 guaranteed.

---

## Strategy 3: Nifty Sector Momentum Alignment

### Concept
Never trade an isolated stock against its parent sector. A trade has an 80%+ higher probability of success when the stock, its sectoral index, and the benchmark Nifty 50 are all moving in the same direction.

### Sector Matching Matrix
| Stock | Sector Index | Key Catalyst |
| :--- | :--- | :--- |
| `TATASTEEL`, `JSWSTEEL` | **Nifty Metal** | Global commodity prices & China cues |
| `SBIN`, `PNB`, `BANKBARODA`| **Nifty PSU Bank** | RBI policy, credit growth & yields |
| `TATAMOTORS`, `M&M` | **Nifty Auto** | Monthly dispatch numbers & demand |
| `WIPRO`, `INFY` | **Nifty IT** | US Tech earnings & NASDAQ performance |

### Alignment Checklist
- [ ] Benchmark Nifty 50 is trading above its VWAP.
- [ ] The stock's Sectoral Index is in the top 3 performing sectors of the day.
- [ ] Stock is outperforming its sector index (Relative Strength > 0).
