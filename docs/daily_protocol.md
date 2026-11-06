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

## 🚫 Ethical Negative Screening Rule (Mandatory & Permanent)
- **Strict Prohibition**: The system strictly excludes companies in **tobacco (e.g. ITC), alcohol, gambling, or related predatory businesses**.
- Such stocks will **never** be shortlisted, analyzed for entry, or traded under any circumstances, regardless of technical momentum.

---

## 📈 Continuous Strategy Evolution & Profit Optimization

A core directive of this partnership is **continual refinement to maximize profitability**:
1. **The Dual-Basket Hedging Edge (Learned Nov 6, 2026)**:
   - When capital allows (₹3,000+), splitting exposure across two uncorrelated sector leaders (e.g., Tech + Consumption) eliminates single-sector drag. Even when one sector consolidates (WIPRO -1.4%), the other surges (ETERNAL +1.7%), preserving positive net portfolio equity (+₹10.05).
2. **The Delivery Swing Edge over Intraday MIS**:
   - Trading in `NSE · DELIVERY` eliminates broker 3:15 PM auto-square-off pressure. Intraday noise can be held into multi-day swing targets, allowing full institutional expansion to play out.
3. **Muhurat Trading Protocol (Diwali Special Session)**:
   - **Market Microstructure**: 1-hour auspicious ceremonial session with >80% historical green close rate, virtually zero institutional dumping, and elevated retail buying spikes.
   - **Pre-Muhurat Action Plan**: Review pre-open matching 15 minutes before the session starts (e.g. 2:05 PM – 2:15 PM). Set resting limit sell orders at target zones to capture liquidity spikes without manual chasing.
4. **Trade Post-Mortems & Risk Budgeting**:
   - As bankroll compounds into higher tiers (₹3,000 ➔ ₹5,000), single-trade risk expands proportionally (₹45 ➔ ₹75), accelerating account growth safely under the 1.5% rule.

