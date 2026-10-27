---
name: india-trader
description: >-
  End-to-end autonomous trading analysis, risk management, and pre-market strategy runbook for the Indian Stock Market (NSE/BSE) using Upstox API v2. Use when analyzing Indian equities, generating the 9:00 AM IST pre-market action plan, managing a ₹2,000 compounding ledger, or setting up the India Trader agent.
metadata:
  icon: trending_up
---

# India Trader (NSE / BSE) Runbook & Knowledge Base

This skill provides an institutional-grade operational guide for analyzing Indian equities on the **National Stock Exchange (NSE)** and **Bombay Stock Exchange (BSE)** using **Upstox API v2**.

---

## 1. Core Operating Tenets

1. **Read-Only Safety Shield**:
   - The agent strictly performs **market analytics, technical scans, and risk calculations**.
   - The agent **never executes real orders** on the broker account. The user executes trades manually in the Upstox app.
2. **Capital Baseline & Risk Governance (₹2,500.00 Baseline)**:
   - All trade recommendations, position sizes, risk budgets, and performance metrics are calculated starting from **₹2,500.00**.
   - Maximum risk per trade is strictly capped at **1.5% (₹37.50)**.
   - Maximum capital deployed in any single stock is **80% (₹2,000.00)**, maintaining a ₹500.00 (20%) cash safety reserve.
   - Dynamic Sector Relative-Strength Scoring is active across all scans (prioritizes #1 leading sector like Nifty IT).
3. **9:00 AM IST Pre-Market Rhythm**:
   - The daily workflow begins at **9:00 AM IST** (during the NSE Pre-Open auction window) to prepare an action plan before the 9:15 AM opening bell.

---

## 2. References & Detailed Documentation

Before implementing or running workflows, refer to the detailed sub-documentation in `references/`:

- **[Upstox API v2 Technical Guide](references/upstox_api_guide.md)**: OAuth2 token generation, market quotes, historical candle bars, and Python client implementation.
- **[₹2,000 Capital & Risk Playbook](references/risk_and_capital_management.md)**: Exact position sizing formulas, max drawdown stops, and compounding progression.
- **[Indian Equity Strategy Playbook](references/strategy_playbook.md)**: 15-Minute ORB, 30-Minute Trend Pullback, and Sector Alignment rules.
- **[Architecture & Database Schema](references/architecture_and_db.md)**: Full project directory layout and SQLite schema for `data/india_trader.db`.

---

## 3. Daily 9:00 AM Pre-Market Workflow (Step-by-Step)

### Step 1: Market State & Macro Cue Check (9:00 – 9:05 AM IST)
1. Verify Upstox API connectivity and access token validity.
2. Check market status via `GET https://api.upstox.com/v2/market/status/NSE`.
3. Check global cues: GIFT Nifty trend, US closing action (S&P 500, NASDAQ), and crude oil prices.

### Step 2: Multi-Timeframe Watchlist Scan (9:05 – 9:10 AM IST)
Scan the liquid NSE sub-₹1,500 watchlist:
`TATASTEEL`, `ZOMATO`, `ITC`, `SBIN`, `TATAMOTORS`, `WIPRO`, `COALINDIA`, `NTPC`.

1. **Daily Chart Trend Filter**:
   - Verify `Daily Close > 20 EMA` and `Daily RSI(14) > 50`.
   - Reject any stock in a daily downtrend (prevents catching falling knives).
2. **Intraday 30-Minute Momentum Check**:
   - Look for price holding above the 21 EMA with RSI bouncing out of the 42–50 pullback zone.

### Step 3: Position Sizing for ₹2,000 Bankroll (9:10 – 9:12 AM IST)
For each qualifying setup:
1. Determine **Entry Price ($P_E$)**, **Stop Loss ($P_{SL}$)**, and **Target ($P_T$)**.
2. Verify Risk/Reward $\ge$ **1:2.0**.
3. Calculate quantity:
   $$\text{Risk Budget} = \text{Current Capital} \times 0.015 = ₹30.00$$
   $$\text{Qty} = \min\left(\left\lfloor \frac{30}{|P_E - P_{SL}|} \right\rfloor, \left\lfloor \frac{\text{Current Capital} \times 0.80}{P_E} \right\rfloor\right)$$

### Step 4: Present Daily Action Card (9:12 AM IST)
Deliver the structured morning plan to the user:
```markdown
# 🇮🇳 Daily Action Card (NSE Pre-Market)
Capital: ₹2,000.00 | Max Risk: ₹30.00 | Reserve Cash: ₹400.00

🎯 Stock: TATA STEEL (NSE: TATASTEEL)
• Setup: 30-Min Pullback Bounce in Daily Uptrend
• Action: BUY
• Entry Range: ₹156.00 – ₹156.30
• Stop Loss: ₹153.50 (Risk: ₹2.50 / share)
• Target: ₹161.50 (Reward: ₹5.50 / share | 1:2.2 R:R)
• Quantity: 10 shares
• Capital Deployed: ₹1,560.00 (Total Risk: ₹25.00 / 1.25%)
```

### Step 5: User Execution & Ledger Recording (9:15 AM onward)
1. The user manually executes the trade in their Upstox trading app.
2. The user informs the agent: *"Bought 10 shares of TATASTEEL at 156.10"*.
3. The agent records the position in `data/india_trader.db` with exact entry, stop loss, and target.

### Step 6: Scaled-Out Profit Shield Activation (Intraday)
When the stock moves **+1.2% to +1.5% into profit**:
- **Step 1 (Bank Profit)**: Prompt user to square off **50% of the position** to lock in guaranteed cash gains into the ledger.
- **Step 2 (Zero-Risk Runner)**: Move the Stop Loss on the remaining 50% to **Break-Even (Entry Price)** in Upstox to guarantee zero-loss risk.
- Record the partial fill and stop adjustment in `data/india_trader.db`.

---

## 4. End-of-Day Review (3:35 PM IST)

At the 3:30 PM market close:
1. Compute today's realized and unrealized P&L in INR.
2. Update the capital balance in `data/india_trader.db`:
   $$\text{New Capital} = \text{Previous Capital} + \text{Realized P&L}$$
3. Record a snapshot in `daily_snapshots`.
4. Print the daily compounding summary and equity curve update.
