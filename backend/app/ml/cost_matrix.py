from typing import Dict, List, Any
import numpy as np
from app.core.config import settings

def calculate_economic_cost(
    y_true: List[int],
    y_scores: List[float],
    threshold: float,
    margin_loss_pct: float = None,
    avg_ticket_size: float = None,
    investigation_cost: float = None
) -> Dict[str, Any]:
    """
    Calculates the total business economic cost at a given threshold.
    Cost = (False Positives * Merchant Margin Loss) + (False Negatives * Fraud Loss) + (Flagged Count * Triage Cost)
    """
    margin = margin_loss_pct or settings.FALSE_POSITIVE_COST_MARGIN
    ticket = avg_ticket_size or settings.AVERAGE_TICKET_SIZE
    triage = investigation_cost or settings.FRAUD_INVESTIGATION_COST

    fp_cost_per_tx = ticket * margin
    fn_cost_per_tx = ticket  # Full transaction amount lost to fraud + chargeback fee

    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for yt, score in zip(y_true, y_scores):
        pred = 1 if score >= threshold else 0
        if yt == 1 and pred == 1:
            tp += 1
        elif yt == 0 and pred == 1:
            fp += 1
        elif yt == 0 and pred == 0:
            tn += 1
        elif yt == 1 and pred == 0:
            fn += 1

    total_fp_loss = fp * fp_cost_per_tx
    total_fn_loss = fn * fn_cost_per_tx
    total_triage_cost = (tp + fp) * triage
    total_economic_loss = total_fp_loss + total_fn_loss + total_triage_cost

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "threshold": round(threshold, 2),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "fp_loss_inr": round(total_fp_loss, 2),
        "fn_loss_inr": round(total_fn_loss, 2),
        "triage_cost_inr": round(total_triage_cost, 2),
        "total_cost_inr": round(total_economic_loss, 2)
    }

def generate_cost_curve(
    y_true: List[int],
    y_scores: List[float],
    margin_loss_pct: float = None,
    avg_ticket_size: float = None
) -> Dict[str, Any]:
    """
    Computes the cost curve across 20 threshold points (0.05 to 0.95)
    to find the optimal decision boundary that minimizes financial loss.
    """
    thresholds = np.linspace(0.05, 0.95, 19)
    curve_points = []
    min_cost = float("inf")
    optimal_threshold = 0.50

    for t in thresholds:
        pt = calculate_economic_cost(
            y_true, y_scores, t,
            margin_loss_pct=margin_loss_pct,
            avg_ticket_size=avg_ticket_size
        )
        curve_points.append(pt)
        if pt["total_cost_inr"] < min_cost:
            min_cost = pt["total_cost_inr"]
            optimal_threshold = pt["threshold"]

    return {
        "optimal_threshold": optimal_threshold,
        "min_cost_inr": round(min_cost, 2),
        "points": curve_points
    }
