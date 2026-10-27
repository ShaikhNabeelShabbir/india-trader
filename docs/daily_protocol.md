# 🇮🇳 Daily Trading Protocol & Collaboration Playbook

This document defines the daily operating rhythm and partnership between the **Trader (User)** and the **India Trader AI Agent**.

---

## ⏰ Daily Operational Timeline (IST)

### 1. 09:00 AM – 09:14 AM IST | Morning Briefing & Strategic Discussion
- **Market State & Macro Check**:
  - Global sentiment, GIFT Nifty opening indication, and Nifty 50 / Bank Nifty technical levels.
  - Sectoral momentum ranking (Nifty Metal, PSU Bank, Auto, IT, FMCG).
- **The Daily Action Card**:
  - Top 1–2 qualifying stock setups from the liquid NSE watchlist.
  - Technical rationale (Daily 20 EMA trend + 30-min pullback or 15-min ORB).
  - Exact **Entry Price Range**, **Stop Loss Price**, and **Target Price** (Minimum 1:2.0 R:R).
  - Exact **Order Quantity** calculated for the ₹2,000 capital bankroll (Max 1.5% / ₹30 risk, max 80% / ₹1,600 capital deployed).
- **Interactive Review**:
  - We discuss and align on which trade to take before market open.

---

### 2. 09:15 AM IST | Market Open & Manual Execution
- **Strict Read-Only Shield**: The agent NEVER places orders automatically.
- **Trader Action**: You manually enter the order in your Upstox mobile or web app based on our agreed plan.
- **Log Entry**: You send a message in chat:
  > *"Bought [QTY] shares of [SYMBOL] at ₹[PRICE]"*
- **Database Entry**: The agent records the trade in `data/india_trader.db` with trade ID, entry timestamp, and targets.

---

### 3. Intraday | Profit Shield & Risk Management
- **The Scaled-Out Profit Shield (+1.2% to +1.5% Rule)**:
  - When the stock gains **+1.2% to +1.5%** from the entry price:
    - **Step 1 (Bank Profit)**: Sell **50% of the position** to lock in guaranteed profit into the cash ledger.
    - **Step 2 (Zero-Risk Runner)**: Modify the Stop Loss on the remaining 50% to **Break-Even (Entry Price)**.
    - **Result**: Even if the market pulls back, you have booked guaranteed cash profit, and the remaining runner has **₹0 risk**.
- **Target Execution**:
  - Ride the remaining 50% runner into **Target 1 (1:2.0 R:R)** or **Target 2 (1:3.0 R:R)**.

---

### 4. 03:30 PM – 03:40 PM IST | Market Close & Compounding Review
- We close any remaining intraday positions.
- The agent computes:
  - Daily realized P&L (₹).
  - Account capital update (Compounding progression).
  - Daily equity snapshot logged to `daily_snapshots` table.
- Print the updated compounding milestone progress.

---

## 📈 Continuous Strategy Evolution & Profit Optimization

A core directive of this partnership is **continual refinement to maximize profitability**:
1. **Trade Post-Mortems**:
   - Review winning trades: What made the entry clean? Could we have trailed the stop higher for extra gains?
   - Review losing / scratched trades: Was there adverse sectoral news? Did we enter too close to resistance?
2. **Dynamic Strategy Tuning**:
   - Calibrate indicator thresholds (e.g. RSI bands, 20 EMA vs 9 EMA pullback sensitivity).
   - Adapt to changing market regimes (low volatility consolidation vs high momentum trending days).
   - Expand our liquid watchlist as capital compounds into higher tiers (e.g., ₹2,500 ➔ ₹3,000 ➔ ₹5,000).
3. **Compounding Acceleration**:
   - As our bankroll grows from ₹2,000, our 1.5% risk budget expands proportionally (₹30 ➔ ₹45 ➔ ₹60), enabling larger position sizes and accelerating account growth safely without taking excessive risk.

