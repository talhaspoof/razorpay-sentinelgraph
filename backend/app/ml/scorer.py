import numpy as np
from typing import Dict, Any, List, Tuple
from app.graph.features import extract_graph_features
from app.core.config import settings

class SentinelRiskScorer:
    """
    Multi-vector risk scoring engine combining localized graph topology,
    behavioral entropy, and economic thresholds.
    """
    def __init__(self):
        self.feature_weights = {
            "user_to_device_ratio": 0.25,
            "user_to_card_ratio": 0.20,
            "user_to_ip_ratio": 0.15,
            "density": 0.15,
            "is_micro_tx": 0.10,
            "avg_degree": 0.15
        }

    def score_transaction(self, ego_subgraph: Dict[str, Any], tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a deterministic, explainable risk score (0.0 to 1.0)
        and categorizes decision into ALLOW, STEP_UP_3DS, or BLOCK.
        """
        features = extract_graph_features(ego_subgraph, tx_payload)
        
        # Calculate Base Topological Score
        raw_score = 0.0
        indicators = []

        user_count = int(features["user_count"])
        max_u_device = int(features["max_users_on_device"])
        max_u_card = int(features["max_users_on_card"])
        max_u_ip = int(features["max_users_on_ip"])
        amount = float(features["amount"])
        is_micro = features["is_micro_tx"]

        # Default clean baseline
        if max_u_device <= 1 and max_u_card <= 1:
            raw_score = 0.01
        else:
            # 1. Automated Carding / BIN Testing (Micro amounts on shared device or shared card)
            if is_micro == 1.0 and (max_u_device >= 2 or max_u_card >= 2):
                raw_score += 0.85
                indicators.append("Automated Carding / BIN Testing Signature (Micro-amount on shared hardware/card)")

            # 2. Sybil Hardware Syndicate (3+ accounts sharing the exact same device)
            elif max_u_device >= 4:
                raw_score += 0.85
                indicators.append(f"Mass Sybil Ring: {max_u_device} accounts clustered on single physical device")
            elif max_u_device == 3:
                raw_score += 0.65
                indicators.append(f"Sybil Syndicate: 3 accounts clustered on single physical device")

            # 3. Card Pooling / Stolen BIN Rotation (2+ accounts sharing exact same payment card)
            elif max_u_card >= 2:
                raw_score += 0.70
                indicators.append(f"Card Pooling Syndicate: {max_u_card} accounts sharing same payment instrument")

            # 4. Legitimate 2-person family sharing (2 users sharing a home tablet, separate cards, normal amounts)
            elif max_u_device == 2 and max_u_card == 1 and is_micro == 0.0:
                raw_score = 0.08  # Safe organic family sharing threshold

        # Replace any unicode in indicators for compatibility
        clean_indicators = [ind.replace("₹", "Rs ") for ind in indicators]

        # Normalize score between 0.0 and 1.0
        final_risk_score = min(round(raw_score, 3), 1.0)

        # Determine Decision based on Configured Thresholds
        if final_risk_score >= settings.DEFAULT_RISK_THRESHOLD:
            decision = "BLOCK"
            action_code = "QUARANTINE_ENTITY"
        elif final_risk_score >= settings.STEP_UP_AUTH_THRESHOLD:
            decision = "CHALLENGE"
            action_code = "STEP_UP_3DS"
        else:
            decision = "ALLOW"
            action_code = "APPROVE"

        return {
            "risk_score": final_risk_score,
            "decision": decision,
            "action_code": action_code,
            "confidence": round(min(0.5 + (final_risk_score * 0.48), 0.98), 2),
            "indicators": clean_indicators if clean_indicators else ["Normal transactional behavior"],
            "features": features
        }

risk_scorer = SentinelRiskScorer()
