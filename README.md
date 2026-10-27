# 🇮🇳 India Trader — Autonomous Indian Stock Market Agent

Institutional-grade quantitative analysis, risk management, and pre-market strategy system for the National Stock Exchange (**NSE**) and Bombay Stock Exchange (**BSE**) using **Upstox API v2**.

---

## 🛡️ Core Tenet: Read-Only Safety Shield
- **100% Read-Only**: The agent only reads market quotes, index levels, and historical candle bars.
- **No Automated Execution**: The agent **never places, modifies, or cancels orders** on your broker account.
- **Manual Execution**: All orders are placed manually by you in your Upstox mobile or web app.

---

## 💰 Capital Governance (₹2,000 Starting Baseline)
- **Initial Capital**: ₹2,000.00 INR
- **Max Risk Per Trade**: 1.5% (Strict ₹30.00 max risk)
- **Max Capital Allocation**: 80% (Max ₹1,600.00 deployed in any single trade)
- **Cash Reserve Buffer**: 20% (₹400.00 kept in cash)
- **Minimum Risk-to-Reward**: 1:2.0
- **The Profit Shield**: When price advances by +1.0%, stop loss is moved to break-even (risk-free).

---

## 🚀 Quick Start CLI Commands

### 1. Run Pre-Flight System Diagnostics
```bash
python3 main.py check
```

### 2. Run 9:00 AM Pre-Market Briefing
```bash
python3 main.py briefing
```

### 3. View Compounding Ledger & Account Balance
```bash
python3 main.py ledger
```

### 4. Check Profit Shield (Break-Even Trigger)
```bash
python3 main.py profit-shield
```

### 5. Record a Manually Executed Trade
```bash
python3 main.py log-trade --symbol WIPRO --qty 7 --entry 182.14 --sl 178.28 --target 190.63
```

### 6. Record Trade Close & Calculate P&L
```bash
python3 main.py close-trade --id 1 --exit 190.60
```
