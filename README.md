# SentinelGraph: Real-Time Graph Anomaly & Sybil Defense for Razorpay

**Razorpay AI Builder Internship 2026 Submission — Track 2: AI Risk Manager**  
*Built by Talha Anwar Ansari*

---

### What is SentinelGraph?

In high-throughput payment gateways, traditional fraud systems evaluate transactions one row at a time. This creates a massive blindspot for **coordinated multi-account fraud syndicates** (e.g. carding botnets, promo abusers, and collusive return rings). To an isolated model, each individual transaction looks completely legitimate.

**SentinelGraph** solves this by converting incoming payment streams into a real-time bipartite relationship graph. It uncovers hidden connections between synthetic user profiles, hardware canvas fingerprints, card BINs, and IP subnets in **sub-millisecond time (`0.88ms`)**, well within Razorpay's 15ms gateway SLA.

---

### Key Engineering Highlights

* **Sub-Millisecond Pre-Auth Scoring (`0.88ms`)**: Extracts a localized 2-hop ego-graph synchronously on every payment intent, enabling real-time blocking before funds or promo credits are lost.
* **Zero False Positives on Organic Indian Networks (`100% Precision`)**: Solves the classic "Hostel Wi-Fi" and "Family iPad" dilemma. Instead of naively flagging shared IPs or shared devices, SentinelGraph checks direct bipartite degree mappings (`max_users_on_device` vs `max_users_on_card`). Fifty students sharing a hostel Wi-Fi are correctly recognized as benign; only genuine multi-account hardware clustering is flagged.
* **Autonomous AI Forensic Investigator**: Ingests graph topology to write clear human-readable attack narratives, maps tactics to MITRE ATT&CK, and auto-compiles bank-ready **Razorpay Dispute Defense Packs** with deterministic hardware telemetry.
* **Economic Cost Matrix Optimization**: Directly models merchant margin loss against fraud slippage to compute the mathematically optimal decision boundary.
* **Interactive Threat Operations Console (SOC)**: Real-time force-directed canvas (Vis.js), live syndicate isolation feed, threat co-pilot, and live webhook injection simulator.

---

### Architecture at a Glance

```
[ Incoming Razorpay Webhook / Payment Intent ]
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Synchronous Pre-Auth Gate (<0.9ms Latency)               │
│ • Validates HMAC-SHA256 signature                           │
│ • Extracts 2-hop ego-graph (excludes merchant mega-hubs)    │
│ • Evaluates bipartite degree features (device/card pooling) │
│ • Decision: ALLOW | STEP-UP 3DS CHALLENGE | BLOCK           │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Risk > Threshold)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Autonomous Forensic & Dispute Layer                      │
│ • Synthesizes attack vectors (Carding, Promo Sybil, RTO)    │
│ • Maps to MITRE ATT&CK taxonomy & extracts verified IOCs    │
│ • Auto-generates structured Razorpay Dispute Dossier        │
│ • Appends to tamper-evident SHA-256 hash-chained ledger     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Asynchronous Community Isolation (Louvain Engine)        │
│ • Isolates dormant, multi-hop syndicates globally           │
│ • Updates central quarantine registry for Hop-0 blocking    │
└─────────────────────────────────────────────────────────────┘
```

---

### Benchmark & Evaluation Results

Evaluated on a held-out test dataset of **1,112 transactions** (1,000 organic transactions with realistic family sharing + 112 injected ground-truth fraud attempts across 4 attack topologies, including adversarial proxy evasion):

| Metric | Result | Why It Matters |
| :--- | :--- | :--- |
| **Precision** | **100.00%** | Zero false positives on legitimate buyers — zero merchant GMV lost |
| **Recall** | **91.07%** | Intercepts 102 out of 112 syndicate attacks across all topologies |
| **F1-Score** | **95.33%** | High harmonic balance across heavily imbalanced traffic |
| **Avg Scoring Latency** | **0.88 ms** | Far faster than Razorpay's 15ms gateway SLA |
| **P99 Latency** | **2.67 ms** | Sub-3ms stability under peak transaction volume |
| **Isolated Syndicates** | **7 Rings** | Full multi-hop community detection |

*Complete benchmark reproduction code is available in `simulation/evaluate_benchmark.py`.*

---

### Quickstart: Running Locally in 2 Minutes

#### Prerequisites
* Python 3.10+
* Node.js 18+

#### 1. Start the Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```
*API docs available at `http://localhost:8000/docs`*

#### 2. Start the Frontend (Threat SOC Dashboard)
```bash
cd frontend
npm install
npm run dev
```
*Open `http://localhost:3000` in your browser.*

#### 3. Run Benchmark Suite
```bash
python simulation/evaluate_benchmark.py
```

---

### Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── core/          # Config & Webhook HMAC-SHA256 signature verification
│   │   ├── graph/         # NetworkX graph manager, 2-hop ego extraction & Louvain
│   │   ├── ml/            # Multi-vector risk scorer & economic cost matrix
│   │   ├── agent/         # Autonomous AI forensic investigator & dispute generator
│   │   ├── api/           # Webhooks, Graph API, Analytics, and Co-Pilot endpoints
│   │   └── utils/         # Cryptographic SHA-256 hash-chained audit logger
│   └── requirements.txt
├── simulation/
│   ├── generator.py       # Benchmark dataset generator (1000 benign + 4 fraud topologies)
│   ├── attack_scenarios.py# Carding botnet, Promo Sybil, and RTO attack streams
│   ├── evasion_simulator.py # Adversarial proxy rotation & jitter simulation
│   └── evaluate_benchmark.py # Evaluation harness & KPI metric calculator
├── frontend/
│   ├── src/
│   │   ├── components/    # GraphViewer, ThreatFeed, ForensicDossier, Copilot, Metrics
│   │   ├── App.jsx        # Main Threat Operations Console
│   │   └── index.css      # Dark SOC styling & typography
│   └── package.json
├── docs/
│   ├── ARCHITECTURE.md    # Deep-dive technical architecture & graph theory
│   ├── BENCHMARK_REPORT.md# Full quantitative evaluation report
│   └── DEMO_SCRIPT.md     # 5-minute video pitch walkthrough script
└── data/
    ├── benchmark_dataset.csv  # Exported 1,112 transaction benchmark (CSV)
    └── benchmark_dataset.json # Raw benchmark transactions (JSON)
```

---

### Complementing Foundation Models (e.g. Razorpay Vulcan)

Razorpay recently announced **Vulcan**, a breakthrough transformer foundation model trained on billions of single payment events. 

SentinelGraph serves as the specialized **Graph Topology & Autonomous Action Layer** that directly complements models like Vulcan:
1. **Feature Augmentation**: Feeds real-time bipartite degree embeddings (`max_users_on_device`, `subgraph_density`) into foundation transformer attention heads.
2. **Multi-Account Fusion**: Catches distributed Sybil rings where each individual transaction looks clean in isolation.
3. **Actionable Forensics**: Translates raw probability scores into explainable dispute defense dossiers for merchants.

---

### License & Compliance
This project is strictly **defense-only** and complies with PCI-DSS guidelines by using synthetic benchmark data, tokenized card references, and immutable cryptographic audit logging.
