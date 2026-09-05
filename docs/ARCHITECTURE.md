# SentinelGraph Architecture & Technical Specification

## 1. Threat Landscape & Problem Definition
In high-throughput payment gateways like Razorpay, automated fraud syndicates execute multi-account attacks across disparate identities:
- **Carding & BIN Testing**: Distributing stolen card numbers across 20+ disposable user accounts to validate micro-charges.
- **Promo & Referral Exploitation**: Re-using device canvas hashes and /24 residential IP subnets to drain merchant marketing budgets.
- **Collusive RTO Scams**: Coordinating Cash-on-Delivery orders to altered physical addresses before initiating fraudulent returns.

Traditional single-row classifiers (e.g. XGBoost on isolated transaction rows) fail because each transaction in isolation looks legitimate. SentinelGraph models the **global bipartite relationship topology** to expose hidden collusion in sub-millisecond real time.

---

## 2. Dual-Tier Graph Architecture

```
[ Incoming Razorpay Webhook / Payload ]
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ Tier 1: Real-Time 2-Hop Ego-Graph Scoring (<1ms Gateway SLA)   │
│ • Filters out merchant mega-hubs to avoid false-positive bridges│
│ • Extracts direct bipartite entity sharing degrees:             │
│   - max_users_on_device, max_users_on_card, max_users_on_ip     │
│ • Computes Shannon entropy over device and IP distributions     │
│ • Evaluates multi-vector Sybil risk score                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Tier 2: Asynchronous Global Community Isolation (Louvain)      │
│ • Computes global connected components across entity subgraph   │
│ • Identifies multi-hop syndicates and collusion density         │
│ • Updates central quarantine registry                           │
└──────────────────────────────┬──────────────────────────────────┘
                               │ (Flagged Clusters)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Tier 3: Autonomous AI Forensic Agent (Reasoning & Evidence)     │
│ • Ingests subgraph topology and temporal event stream           │
│ • Maps IOCs to MITRE ATT&CK taxonomy                            │
│ • Auto-generates structured Razorpay Dispute Defense Packs      │
│ • Logs tamper-evident hash-chained audit trails                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Mathematical & Algorithmic Foundations

### 3.1 Bipartite Entity Degree Feature Extraction
To prevent the "Hostel Wi-Fi" and "Family iPad" false-positive traps:
$$\text{MaxUsersOnDevice} = \max_{d \in \text{Devices}(G_{\text{ego}})} \deg_{\text{user}}(d)$$
$$\text{MaxUsersOnCard} = \max_{c \in \text{Cards}(G_{\text{ego}})} \deg_{\text{user}}(c)$$

- $\text{MaxUsersOnDevice} \ge 3 \implies \text{Sybil Syndicate}$
- $\text{MaxUsersOnCard} \ge 2 \implies \text{Card Pooling Fraud}$
- $\text{MaxUsersOnIP} \ge 10 \text{ but } \text{MaxUsersOnDevice} = 1 \implies \text{Benign Shared Wi-Fi}$

### 3.2 Shannon Attribute Entropy
$$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$
Low entropy across high transaction volume signifies automated bot activity.

### 3.3 Economic Cost Matrix
$$\text{Total Cost} = (\text{FP} \times \text{Ticket} \times \text{MarginLoss}) + (\text{FN} \times \text{Ticket}) + ((\text{TP} + \text{FP}) \times \text{TriageCost})$$
Dynamic threshold tuning finds the global minimum of this cost surface based on the merchant's margin profile.

---

## 4. Cryptographic Audit Trail
Every AI decision and quarantine action is signed and hash-chained in an append-only JSON-L ledger:
$$\text{Hash}_i = \text{SHA256}(\text{Event}_i \mathbin{\Vert} \text{Hash}_{i-1})$$
Ensures verifiable, tamper-evident records for regulatory compliance.
