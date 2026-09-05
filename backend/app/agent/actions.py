from typing import Dict, Any, List
import time
from app.graph.engine import graph_engine
from app.utils.audit_logger import audit_logger

class BoundedActionEngine:
    """
    Executes bounded, auditable defensive actions for flagged entities and clusters.
    All actions are gated and recorded in the cryptographic audit trail.
    """
    
    @staticmethod
    def execute_quarantine(node_id: str, reason: str, agent_confidence: float) -> Dict[str, Any]:
        """
        Quarantines a specific suspicious entity node (User, Device, Card, IP).
        """
        success = graph_engine.quarantine_node(node_id, reason=reason)
        event_record = {
            "action": "QUARANTINE_ENTITY",
            "target_node": node_id,
            "reason": reason,
            "confidence": agent_confidence,
            "success": success,
            "executed_at": time.time()
        }
        audit_logger.log_event("ENTITY_QUARANTINED", event_record, actor="SentinelAI_ActionEngine")
        return event_record

    @staticmethod
    def execute_cluster_isolation(cluster_id: str, node_ids: List[str], reason: str, agent_confidence: float) -> Dict[str, Any]:
        """
        Isolates an entire coordinated fraud syndicate.
        """
        cluster_info = graph_engine.quarantine_cluster(cluster_id, node_ids, reason=reason)
        event_record = {
            "action": "ISOLATE_FRAUD_RING",
            "cluster_id": cluster_id,
            "isolated_nodes_count": len(cluster_info["node_ids"]),
            "reason": reason,
            "confidence": agent_confidence,
            "executed_at": time.time()
        }
        audit_logger.log_event("CLUSTER_ISOLATED", event_record, actor="SentinelAI_ActionEngine")
        return event_record

    @staticmethod
    def generate_dispute_defense_dossier(tx_id: str, user_id: str, ego_subgraph: Dict[str, Any], attack_summary: str) -> Dict[str, Any]:
        """
        Auto-generates a structured Razorpay Dispute & Chargeback Evidence Dossier.
        """
        metrics = ego_subgraph.get("metrics", {})
        dossier = {
            "dossier_id": f"disp_dossier_{tx_id}",
            "disputed_transaction_id": tx_id,
            "user_id": user_id,
            "forensic_evidence": {
                "attack_vector_summary": attack_summary,
                "connected_entities": metrics.get("node_count", 0),
                "device_sharing_evidence": f"{metrics.get('user_count', 0)} accounts on {metrics.get('device_count', 0)} devices",
                "ip_correlation": f"{metrics.get('ip_count', 0)} IP addresses involved",
                "card_fingerprints": f"{metrics.get('card_count', 0)} distinct card tokens"
            },
            "recommended_bank_narrative": (
                f"Transaction {tx_id} by {user_id} is part of a verified coordinated fraud syndicate. "
                f"Telemetry confirms {metrics.get('node_count', 0)} linked entities across shared hardware and IP subnets. "
                "Evidence strongly refutes claims of unauthorized third-party charge."
            ),
            "generated_at": time.time()
        }
        audit_logger.log_event("DISPUTE_DOSSIER_GENERATED", dossier, actor="SentinelAI_DisputeGuard")
        return dossier

action_engine = BoundedActionEngine()
