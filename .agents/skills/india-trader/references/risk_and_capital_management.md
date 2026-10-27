# ₹2,000 Capital & Risk Management Playbook

This document defines the mathematical risk rules, position sizing formulas, and compounding principles for trading Indian equities starting with an initial bankroll of **₹2,000 INR**.

---

## 1. The Core Philosophy

When trading with small capital (₹2,000), the number one objective is **capital preservation through asymmetric risk-to-reward**. You cannot afford large drawdowns, but a high win-rate strategy with 1:2.0 risk-reward will compound capital rapidly.

---

## 2. Hardcoded Capital Parameters

| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| **Initial Capital** | **₹2,000.00** | Starting ledger baseline |
| **Max Risk Per Trade** | **1.5% to 2.0%** | **₹30.00 to ₹40.00** max dollar risk per trade |
| **Max Capital Allocation** | **80% (₹1,600.00)** | Never deploy 100% of capital in a single stock |
| **Cash Buffer** | **20% (₹400.00)** | Cash reserve for brokerage/STT fees and liquidity |
| **Minimum Risk/Reward** | **1:2.0** | For every ₹1.00 at risk, target at least ₹2.00 profit |
| **Max Daily Loss Limit** | **4.0% (₹80.00)** | If down ₹80 in a single day, stop trading immediately |

---

## 3. Position Sizing Formula

The agent determines the exact number of shares to purchase using this two-step formula:

### Step 1: Calculate Dollar Risk Budget
$$\text{Risk Budget (₹)} = \text{Current Capital} \times \left(\frac{\text{Risk Pct}}{100}\right)$$
For ₹2,000 capital at 1.5% risk:
$$\text{Risk Budget} = 2000 \times 0.015 = ₹30.00$$

### Step 2: Calculate Risk Per Share
$$\text{Risk Per Share (₹)} = |\text{Entry Price} - \text{Stop Loss Price}|$$

### Step 3: Determine Share Quantity
$$\text{Qty}_{\text{risk}} = \left\lfloor \frac{\text{Risk Budget}}{\text{Risk Per Share}} \right\rfloor$$
$$\text{Qty}_{\text{allocation}} = \left\lfloor \frac{\text{Current Capital} \times 0.80}{\text{Entry Price}} \right\rfloor$$
$$\text{Final Quantity} = \max\left(1, \min(\text{Qty}_{\text{risk}}, \text{Qty}_{\text{allocation}})\right)$$

### Real Example: Tata Steel (`TATASTEEL`)
- Current Capital: ₹2,000.00
- Entry Price: ₹156.00
- Stop Loss: ₹153.50 (Risk per share = ₹2.50)
- Target: ₹161.50 (Reward per share = ₹5.50 | R:R = 1:2.2)
- $\text{Qty}_{\text{risk}} = \lfloor 30.00 / 2.50 \rfloor = 12 \text{ shares}$
- Capital required for 12 shares: $12 \times 156.00 = ₹1,872.00$
- Max allocation limit (80% of ₹2,000): ₹1,600.00
- $\text{Qty}_{\text{allocation}} = \lfloor 1600 / 156.00 \rfloor = 10 \text{ shares}$
- **Final Order Recommendation**: **10 shares**
  - Total Capital Deployed: ₹1,560.00
  - Actual Capital at Risk: $10 \times 2.50 = ₹25.00$ (1.25% of capital)
  - Potential Profit: $10 \times 5.50 = ₹55.00$ (+2.75% account gain)

---

## 4. The Profit Shield (Break-Even Rule)

To prevent winning trades from turning into losses:
1. When a stock advances by **+1.0%** from the entry price:
   - Move the Stop Loss to **Break-Even (Entry Price)**.
   - The trade is now 100% risk-free.
2. When the stock reaches **Target 1 (1:1.5 R:R)**:
   - Close 50% of the position to bank profit.
   - Trail the stop loss on the remaining 50% using the 15-minute 20 EMA.

---

## 5. Compounding Ledger Progression

| Milestone | Total Equity | 1.5% Risk Budget | Max Position (80%) |
| :--- | :--- | :--- | :--- |
| **Starting Capital** | **₹2,000.00** | ₹30.00 | ₹1,600.00 |
| **Stage 1 (+25%)** | **₹2,500.00** | ₹37.50 | ₹2,000.00 |
| **Stage 2 (+50%)** | **₹3,000.00** | ₹45.00 | ₹2,400.00 |
| **Stage 3 (+100%)**| **₹4,000.00** | ₹60.00 | ₹3,200.00 |

Because risk scales proportionally with equity, a losing streak automatically shrinks position size, while winning runs accelerate growth.
