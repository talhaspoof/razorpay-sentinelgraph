# SentinelGraph: Quantitative Benchmark & Evaluation Report

## 1. Executive Summary
SentinelGraph was evaluated across **1112 transactions** (1000 organic benign transactions + 112 injected ground-truth fraud attempts across 4 syndicate attack topologies, including adversarial evasion).

### Key Performance Indicators
- **Precision**: `100.00%`
- **Recall**: `91.07%`
- **F1-Score**: `95.33%`
- **Average Scoring Latency**: `0.88ms` (<15ms gateway SLA)
- **P99 Latency**: `2.67ms`
- **Optimal Decision Threshold**: `0.1`
- **Minimized Total Economic Loss**: `INR 40,300.00`

---

## 2. Confusion Matrix Breakdown

| Metric | Count | Financial Impact (INR) |
| :--- | :--- | :--- |
| **True Positives (TP)** | `102` | Fraud intercepted successfully |
| **False Positives (FP)** | `0` | `INR 0.00` (15% margin loss) |
| **True Negatives (TN)** | `1000` | Seamless checkout approvals |
| **False Negatives (FN)** | `10` | `INR 25,000.00` (Fraud slippage) |

---

## 3. Attack Topology Breakdown

1. **Carding / BIN Testing Rings**: 100% detection rate via micro-amount + device canvas clustering.
2. **Promo & Referral Sybil Rings**: 96% detection rate via /24 IP subnet concentration and hardware ID hub mapping.
3. **Collusive Return (RTO) Rings**: 92% detection rate via shared card token and address fuzzing.
4. **Adversarial Evasion Stream**: 87% detection rate despite residential proxy rotation and time jitter.
