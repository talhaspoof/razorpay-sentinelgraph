import json
import time
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.agent.prompts import SYSTEM_FORENSIC_PROMPT, INVESTIGATION_USER_TEMPLATE
from app.agent.actions import action_engine
from app.utils.audit_logger import audit_logger

class ForensicAgent:
    """
    Autonomous AI Forensic Investigation Agent that analyzes subgraphs,
    synthesizes attack narratives, identifies IOCs, and triggers bounded actions.
    """
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    def investigate(self, tx_payload: Dict[str, Any], ego_subgraph: Dict[str, Any], risk_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a forensic investigation over a flagged transaction and its graph cluster.
        """
        metrics = ego_subgraph.get("metrics", {})
        features = risk_result.get("features", {})
        indicators = risk_result.get("indicators", [])
        
        # Try LLM-based investigation if API key is configured
        llm_response = None
        if self.gemini_key:
            llm_response = self._call_gemini(tx_payload, ego_subgraph, risk_result)
        elif self.openai_key:
            llm_response = self._call_openai(tx_payload, ego_subgraph, risk_result)

        # Use High-Fidelity Deterministic Forensic Reasoner if LLM unavailable
        if not llm_response:
            llm_response = self._deterministic_reasoning(tx_payload, ego_subgraph, risk_result)

        # Automatically trigger bounded actions if severity is high
        action_result = None
        if risk_result.get("decision") == "BLOCK":
            user_node = f"user:{tx_payload.get('user_id')}"
            action_result = action_engine.execute_quarantine(
                node_id=user_node,
                reason=f"Flagged by SentinelAI as {llm_response.get('attack_vector')}",
                agent_confidence=risk_result.get("confidence", 0.90)
            )

        # Generate Dispute Dossier for chargeback readiness
        dispute_dossier = action_engine.generate_dispute_defense_dossier(
            tx_id=tx_payload.get("id", "tx_unknown"),
            user_id=tx_payload.get("user_id", "anon"),
            ego_subgraph=ego_subgraph,
            attack_summary=llm_response.get("threat_summary", "")
        )

        investigation_record = {
            "tx_id": tx_payload.get("id"),
            "user_id": tx_payload.get("user_id"),
            "risk_score": risk_result.get("risk_score"),
            "decision": risk_result.get("decision"),
            "attack_vector": llm_response.get("attack_vector"),
            "threat_summary": llm_response.get("threat_summary"),
            "iocs": llm_response.get("iocs", []),
            "mitre_tactics": llm_response.get("mitre_tactics", []),
            "recommended_action": llm_response.get("recommended_action"),
            "action_executed": action_result,
            "dispute_dossier": dispute_dossier,
            "investigated_at": time.time()
        }

        audit_logger.log_event("INVESTIGATION_COMPLETED", investigation_record, actor="SentinelAI_ForensicAgent")
        return investigation_record

    def _deterministic_reasoning(self, tx_payload: Dict[str, Any], ego_subgraph: Dict[str, Any], risk_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expert-system forensic reasoning engine that mirrors SOC L2 analysis.
        """
        metrics = ego_subgraph.get("metrics", {})
        features = risk_result.get("features", {})
        amount = float(tx_payload.get("amount", 0.0))
        u_d_ratio = features.get("user_to_device_ratio", 1.0)
        u_c_ratio = features.get("user_to_card_ratio", 1.0)
        u_i_ratio = features.get("user_to_ip_ratio", 1.0)
        
        iocs = []
        mitre_tactics = []

        # Classify Attack Vector based on Topological Signatures
        if amount <= 10.0 and u_d_ratio >= 2.0:
            attack_vector = "CARDING_BOTNET"
            mitre_tactics = ["T1110.003 - Password Spraying/Card Testing", "T1078 - Valid Accounts"]
            iocs.append(f"Micro-Transaction Testing (₹{amount}) across {metrics.get('user_count', 0)} synthetic user profiles")
            iocs.append(f"Device Hub: {metrics.get('device_count', 0)} physical hardware fingerprints shared by {metrics.get('user_count', 0)} accounts")
            summary = (
                f"Automated Carding / BIN Enumeration attack detected. {metrics.get('user_count', 0)} accounts are cycling through "
                f"{metrics.get('card_count', 0)} payment instruments via shared hardware ({metrics.get('device_count', 0)} devices) "
                f"to validate stolen cards with low-value ₹{amount} auth attempts."
            )
            rec_action = "QUARANTINE_DEVICE_AND_CARD_BIN"

        elif u_d_ratio >= 2.5 or u_i_ratio >= 3.0:
            attack_vector = "PROMO_SYBIL_RING"
            mitre_tactics = ["T1585 - Establish Accounts", "T1584 - Compromise Infrastructure"]
            iocs.append(f"Sybil Multi-Accounting: {metrics.get('user_count', 0)} users linked to {metrics.get('device_count', 0)} devices")
            iocs.append(f"IP Subnet Concentration: {metrics.get('ip_count', 0)} IP endpoints")
            summary = (
                f"Coordinated Promo & Referral Sybil Ring detected. High entity coupling between {metrics.get('user_count', 0)} user profiles "
                f"sharing {metrics.get('device_count', 0)} device fingerprints. Indicates deliberate coupon/incentive exhaustion."
            )
            rec_action = "ISOLATE_CLUSTER_AND_REVOKE_PROMO"

        elif u_c_ratio >= 2.0:
            attack_vector = "COLLUSIVE_RTO_FRAUD"
            mitre_tactics = ["T1566 - Phishing", "T1078 - Compromised Credentials"]
            iocs.append(f"Payment Instrument Sharing across {metrics.get('user_count', 0)} buyer identities")
            summary = (
                f"Payment Pooling / Collusive Order Ring. Multiple independent user profiles are utilizing the same underlying "
                f"payment card or UPI VPA, indicating return-to-origin fraud or synchronized purchase manipulation."
            )
            rec_action = "TRIGGER_3DS_STEP_UP"

        else:
            attack_vector = "LOW_RISK_ORGANIC"
            summary = "Transaction topology reflects organic customer activity within normal statistical thresholds."
            rec_action = "APPROVE"

        return {
            "attack_vector": attack_vector,
            "threat_summary": summary,
            "iocs": iocs,
            "mitre_tactics": mitre_tactics,
            "recommended_action": rec_action
        }

    def _call_gemini(self, tx_payload: Dict[str, Any], ego_subgraph: Dict[str, Any], risk_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.gemini_key or self.gemini_key.startswith("your_") or len(self.gemini_key) < 20:
            return None
        # Structured Gemini client call with fallback
        try:
            from google import genai
            client = genai.Client(api_key=self.gemini_key)
            prompt = INVESTIGATION_USER_TEMPLATE.format(
                tx_id=tx_payload.get("id"),
                user_id=tx_payload.get("user_id"),
                amount=tx_payload.get("amount"),
                timestamp=tx_payload.get("timestamp"),
                status=tx_payload.get("status"),
                node_count=ego_subgraph.get("metrics", {}).get("node_count"),
                user_count=ego_subgraph.get("metrics", {}).get("user_count"),
                device_count=ego_subgraph.get("metrics", {}).get("device_count"),
                ip_count=ego_subgraph.get("metrics", {}).get("ip_count"),
                card_count=ego_subgraph.get("metrics", {}).get("card_count"),
                density=ego_subgraph.get("metrics", {}).get("density"),
                user_to_device_ratio=risk_result.get("features", {}).get("user_to_device_ratio"),
                user_to_card_ratio=risk_result.get("features", {}).get("user_to_card_ratio"),
                indicators="\n".join(risk_result.get("indicators", [])),
                nodes_sample=json.dumps([n["id"] for n in ego_subgraph.get("nodes", [])[:10]])
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{SYSTEM_FORENSIC_PROMPT}\n\n{prompt}\nRespond in valid JSON with keys: attack_vector, threat_summary, iocs (list), mitre_tactics (list), recommended_action."
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3].strip()
            return json.loads(raw_text)
        except Exception:
            return None

    def _call_openai(self, tx_payload: Dict[str, Any], ego_subgraph: Dict[str, Any], risk_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.openai_key or self.openai_key.startswith("your_") or len(self.openai_key) < 20:
            return None
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            prompt = INVESTIGATION_USER_TEMPLATE.format(
                tx_id=tx_payload.get("id"),
                user_id=tx_payload.get("user_id"),
                amount=tx_payload.get("amount"),
                timestamp=tx_payload.get("timestamp"),
                status=tx_payload.get("status"),
                node_count=ego_subgraph.get("metrics", {}).get("node_count"),
                user_count=ego_subgraph.get("metrics", {}).get("user_count"),
                device_count=ego_subgraph.get("metrics", {}).get("device_count"),
                ip_count=ego_subgraph.get("metrics", {}).get("ip_count"),
                card_count=ego_subgraph.get("metrics", {}).get("card_count"),
                density=ego_subgraph.get("metrics", {}).get("density"),
                user_to_device_ratio=risk_result.get("features", {}).get("user_to_device_ratio"),
                user_to_card_ratio=risk_result.get("features", {}).get("user_to_card_ratio"),
                indicators="\n".join(risk_result.get("indicators", [])),
                nodes_sample=json.dumps([n["id"] for n in ego_subgraph.get("nodes", [])[:10]])
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_FORENSIC_PROMPT},
                    {"role": "user", "content": f"{prompt}\nRespond in valid JSON with keys: attack_vector, threat_summary, iocs (list), mitre_tactics (list), recommended_action."}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return None

forensic_agent = ForensicAgent()
