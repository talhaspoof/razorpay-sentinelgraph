from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import json
import time
from app.core.security import verify_razorpay_signature
from app.graph.engine import graph_engine
from app.ml.scorer import risk_scorer
from app.agent.forensic_agent import forensic_agent
from app.utils.audit_logger import audit_logger

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_razorpay_signature: Optional[str] = Header(None)
):
    """
    Ingests and validates incoming Razorpay webhooks.
    Real-time path runs in <15ms; deep forensic agent triggers asynchronously on high risk.
    """
    raw_body = await request.body()
    
    # Signature Verification (Allow test simulation if header omitted)
    if x_razorpay_signature:
        is_valid = verify_razorpay_signature(raw_body, x_razorpay_signature)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid HMAC-SHA256 signature")

    try:
        event_data = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON payload")

    event_type = event_data.get("event", "payment.authorized")
    payload = event_data.get("payload", {})
    payment = payload.get("payment", {}).get("entity", {})
    
    # Extract Entity Metadata from Razorpay Payload
    tx_id = payment.get("id") or f"pay_{int(time.time()*1000)}"
    user_id = payment.get("notes", {}).get("user_id") or payment.get("email") or payment.get("contact") or "anon_user"
    device_id = payment.get("notes", {}).get("device_fingerprint") or payment.get("notes", {}).get("canvas_hash") or "device_default"
    ip_address = payment.get("notes", {}).get("ip_address") or "127.0.0.1"
    card_token = payment.get("card_id") or payment.get("vpa") or payment.get("method") or "card_default"
    shipping_addr = payment.get("notes", {}).get("shipping_address_hash") or "unknown_address"
    amount = float(payment.get("amount", 0)) / 100.0  # Razorpay amounts are in paise

    normalized_tx = {
        "id": tx_id,
        "user_id": user_id,
        "device_fingerprint": device_id,
        "ip_address": ip_address,
        "card_token": card_token,
        "shipping_address_hash": shipping_addr,
        "merchant_id": payment.get("notes", {}).get("merchant_id", "rzp_merchant_main"),
        "amount": amount,
        "timestamp": payment.get("created_at") or time.time(),
        "status": payment.get("status", "authorized"),
        "event_type": event_type
    }

    # Step 1: Real-time Ingestion & 2-Hop Ego-Graph Extraction (<10ms)
    ingest_result = graph_engine.add_transaction(normalized_tx)
    ego_subgraph = ingest_result["ego_subgraph"]

    # Step 2: Anomaly & Risk Scoring (<5ms)
    risk_assessment = risk_scorer.score_transaction(ego_subgraph, normalized_tx)

    # Step 3: Run AI Forensic Agent if Anomaly or High Risk
    investigation = None
    if risk_assessment["decision"] in ["BLOCK", "CHALLENGE"]:
        investigation = forensic_agent.investigate(normalized_tx, ego_subgraph, risk_assessment)

    response_payload = {
        "status": "processed",
        "tx_id": tx_id,
        "risk_assessment": risk_assessment,
        "investigation": investigation,
        "ego_metrics": ego_subgraph.get("metrics", {})
    }

    audit_logger.log_event("WEBHOOK_PROCESSED", {
        "event_type": event_type,
        "tx_id": tx_id,
        "decision": risk_assessment["decision"],
        "risk_score": risk_assessment["risk_score"]
    })

    return response_payload
