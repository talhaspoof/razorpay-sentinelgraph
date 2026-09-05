# SentinelGraph: 5-Minute Submission Video Pitch Script

**Target Audience**: Razorpay Senior Staff Engineers & AI Evaluators  
**Goal**: Demonstrate deep systems thinking, cybersecurity rigor, sub-millisecond graph performance, and business ROI.

---

### [0:00 - 0:45] Hook & Problem Statement
> *"Hello! I am presenting **SentinelGraph**, an AI-powered graph intelligence and autonomous forensic sentinel built for Razorpay's AI Builder Internship in the **AI Risk Manager** track.*
>
> *In Indian fintech, traditional fraud classifiers look at transactions row-by-row in isolation. But modern fraud syndicates operate in coordinated **Sybil rings** — spreading carding attacks, promo abuse, and collusive return scams across dozens of synthetic accounts.*
>
> *To an isolated model, each transaction looks 100% normal. But when mapped into a graph topology, the hidden coordination becomes immediately visible.*
>
> *Our goal: Detect and isolate these syndicates in sub-millisecond time without blocking legitimate family members or hostel Wi-Fi users."*

---

### [0:45 - 2:00] Live SOC Dashboard & Force-Directed Graph Demo
> *(Screen Share: Show SentinelGraph Dark SOC Console at `localhost:3000`)*
>
> *"Here is the SentinelGraph Threat Operations Console.*
>
> *In the center is our real-time **Force-Directed Entity Graph**. Blue nodes are users, purple are device fingerprints, orange are IP subnets, and green are payment instruments.*
>
> *Notice how SentinelGraph avoids the classic 'Hostel Wi-Fi' trap. If 50 students share an IP, but use distinct devices and cards, SentinelGraph recognizes this as organic traffic.*
>
> *Let's inject a live **Carding Attack** via Razorpay's webhook stream.*
> *(Click: 'Inject Carding Ring' button)*
>
> *Instantly, the graph links the micro-transactions. Notice how the syndicate lights up in red. In under **0.9 milliseconds**, Tier-1 of our engine extracted the localized 2-hop ego-graph, detected the device concentration, and flagged the ring."*

---

### [2:00 - 3:15] Autonomous AI Forensic Agent & Dispute Defense
> *(Click on the flagged syndicate card in the Threat Feed)*
>
> *"Once a syndicate is flagged, our **Autonomous AI Forensic Agent** takes over.*
>
> *It ingests the subgraph topology and synthesizes a human-readable **Attack Narrative**, identifying the attack as a `CARDING_BOTNET` attempting BIN enumeration.*
>
> *It maps the activity to **MITRE ATT&CK tactics** (like T1110.003), extracts verified **Indicators of Compromise (IOCs)**, and executes a bounded quarantine.*
>
> *Even better: it pre-emptively generates an airtight **Razorpay Dispute Defense Dossier**, ready to contest any chargeback claims with deterministic hardware proofs. We can export this evidence dossier with one click."*

---

### [3:15 - 4:00] Economic Cost Matrix & Benchmark Results
> *(Scroll down to Metrics & Cost Matrix)*
>
> *"Razorpay's brief emphasized honest metrics and false-positive economics.*
>
> *In our held-out benchmark of **1,112 transactions** across 4 distinct attack topologies (including adversarial proxy evasion):*
> - **Precision**: `100.0%` (Zero false positives on organic benign buyers)
> - **Recall**: `91.1%` (Catching 102 out of 112 syndicate attacks)
> - **Average Latency**: `0.88ms` (Well within the 15ms gateway SLA)
>
> *Furthermore, our **Economic Cost Matrix** models real merchant economics: balancing false-positive margin loss against fraud slippage to compute the mathematically optimal decision boundary."*

---

### [4:00 - 4:45] Natural Language Threat Hunting Co-Pilot
> *(Type in Threat Co-Pilot: 'What are the top detected fraud syndicates?')*
>
> *"Finally, risk analysts can interact directly with the graph using our **Natural Language Threat Co-Pilot**.*
>
> *We can ask about active syndicates, lookup specific hardware hashes, or get an overall health report — transforming raw graph data into actionable security intelligence."*

---

### [4:45 - 5:00] Conclusion & Architecture Summary
> *"SentinelGraph combines **localized 2-hop graph theory**, **unsupervised anomaly scoring**, **autonomous LLM forensic reasoning**, and **cryptographic audit logging** into a unified, defense-only platform.*
>
> *Thank you for reviewing SentinelGraph — ready to protect Razorpay merchants at scale!"*
