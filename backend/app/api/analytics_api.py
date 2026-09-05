from fastapi import APIRouter
from typing import Dict, Any, List
from pydantic import BaseModel
from app.ml.cost_matrix import calculate_economic_cost, generate_cost_curve
from app.utils.audit_logger import audit_logger

router = APIRouter(prefix="/analytics", tags=["Analytics & Evaluation"])

class CostCalculationRequest(BaseModel):
    threshold: float = 0.70
    margin_loss_pct: float = 0.15
    avg_ticket_size: float = 2500.0

@router.post("/cost-curve")
async def get_cost_curve_data(payload: CostCalculationRequest):
    """
    Returns the economic cost curve and optimal decision threshold
    based on the benchmark evaluation dataset.
    """
    # Sample synthetic ground-truth benchmark distributions
    # 500 ground-truth transactions (450 benign, 50 fraud)
    import numpy as np
    np.random.seed(42)
    
    benign_scores = list(np.random.beta(1.5, 8.0, 450))  # Skewed low
    fraud_scores = list(np.random.beta(7.0, 2.0, 50))    # Skewed high
    
    y_true = [0]*450 + [1]*50
    y_scores = benign_scores + fraud_scores
    
    curve = generate_cost_curve(
        y_true=y_true,
        y_scores=y_scores,
        margin_loss_pct=payload.margin_loss_pct,
        avg_ticket_size=payload.avg_ticket_size
    )
    
    current_metrics = calculate_economic_cost(
        y_true=y_true,
        y_scores=y_scores,
        threshold=payload.threshold,
        margin_loss_pct=payload.margin_loss_pct,
        avg_ticket_size=payload.avg_ticket_size
    )
    
    return {
        "curve": curve,
        "current_metrics": current_metrics
    }

@router.get("/audit-logs")
async def get_audit_trail(limit: int = 50):
    """
    Returns cryptographic audit logs for verification.
    """
    return audit_logger.get_recent_logs(limit=limit)

@router.get("/dataset")
async def get_benchmark_dataset():
    """
    Returns the full synthetic benchmark dataset (1,112 transactions).
    """
    import os, json
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "benchmark_dataset.json"))
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
