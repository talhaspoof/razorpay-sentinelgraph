import numpy as np
from typing import Dict, Any, List
import math

def calculate_entropy(items: List[Any]) -> float:
    """
    Computes Shannon entropy over a list of discrete categorical items.
    Low entropy with high count = high concentration / repetitive bot pattern.
    """
    if not items:
        return 0.0
    total = len(items)
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return round(entropy, 4)

def extract_graph_features(ego_subgraph: Dict[str, Any], tx_payload: Dict[str, Any]) -> Dict[str, float]:
    """
    Extracts high-signal numerical and structural features from a localized ego-subgraph
    and transaction payload for ML anomaly detection.
    """
    metrics = ego_subgraph.get("metrics", {})
    nodes = ego_subgraph.get("nodes", [])
    edges = ego_subgraph.get("edges", [])
    
    node_count = metrics.get("node_count", 0)
    edge_count = metrics.get("edge_count", 0)
    density = metrics.get("density", 0.0)
    user_count = metrics.get("user_count", 0)
    device_count = metrics.get("device_count", 0)
    ip_count = metrics.get("ip_count", 0)
    card_count = metrics.get("card_count", 0)
    
    # Ratios (Structural Anomaly Indicators)
    # If 1 device is linked to 10 users, ratio = 10.0 (Severe Sybil indicator)
    user_to_device_ratio = user_count / max(device_count, 1)
    user_to_card_ratio = user_count / max(card_count, 1)
    user_to_ip_ratio = user_count / max(ip_count, 1)
    
    # Compute actual direct user connectivity per entity (bipartite degree)
    # Count how many users directly connect to each device, card, and IP
    device_user_counts = {}
    card_user_counts = {}
    ip_user_counts = {}
    
    for edge in edges:
        src = edge.get("source", "")
        tgt = edge.get("target", "")
        rel = edge.get("relation", "")
        
        user_node = src if src.startswith("user:") else (tgt if tgt.startswith("user:") else None)
        other_node = tgt if src == user_node else src
        
        if user_node and other_node:
            if other_node.startswith("device:"):
                device_user_counts.setdefault(other_node, set()).add(user_node)
            elif other_node.startswith("payment:"):
                card_user_counts.setdefault(other_node, set()).add(user_node)
            elif other_node.startswith("ip:"):
                ip_user_counts.setdefault(other_node, set()).add(user_node)

    max_users_on_single_device = max([len(u) for u in device_user_counts.values()], default=1)
    max_users_on_single_card = max([len(u) for u in card_user_counts.values()], default=1)
    max_users_on_single_ip = max([len(u) for u in ip_user_counts.values()], default=1)

    # Number of devices/cards shared by 2+ users
    shared_device_count = sum(1 for u in device_user_counts.values() if len(u) >= 2)
    shared_card_count = sum(1 for u in card_user_counts.values() if len(u) >= 2)

    # Collect node degrees
    degrees = [n.get("degree", 0) for n in nodes]
    max_degree = max(degrees) if degrees else 0
    avg_degree = (sum(degrees) / len(degrees)) if degrees else 0
    
    # Calculate attribute entropies across ego-subgraph
    device_ids = [n["id"] for n in nodes if n.get("type") == "device"]
    ip_addrs = [n["id"] for n in nodes if n.get("type") == "ip"]
    card_tokens = [n["id"] for n in nodes if n.get("type") == "payment_method"]
    
    device_entropy = calculate_entropy(device_ids)
    ip_entropy = calculate_entropy(ip_addrs)
    card_entropy = calculate_entropy(card_tokens)
    
    # Transaction Amount & Velocity heuristics
    amount = float(tx_payload.get("amount", 0.0))
    is_micro_tx = 1.0 if 0 < amount <= 10.0 else 0.0
    
    return {
        "node_count": float(node_count),
        "edge_count": float(edge_count),
        "density": float(density),
        "user_count": float(user_count),
        "device_count": float(device_count),
        "ip_count": float(ip_count),
        "card_count": float(card_count),
        "max_users_on_device": float(max_users_on_single_device),
        "max_users_on_card": float(max_users_on_single_card),
        "max_users_on_ip": float(max_users_on_single_ip),
        "shared_device_count": float(shared_device_count),
        "shared_card_count": float(shared_card_count),
        "user_to_device_ratio": float(round(user_to_device_ratio, 2)),
        "user_to_card_ratio": float(round(user_to_card_ratio, 2)),
        "user_to_ip_ratio": float(round(user_to_ip_ratio, 2)),
        "max_degree": float(max_degree),
        "avg_degree": float(round(avg_degree, 2)),
        "device_entropy": float(device_entropy),
        "ip_entropy": float(ip_entropy),
        "card_entropy": float(card_entropy),
        "amount": float(amount),
        "is_micro_tx": is_micro_tx
    }
