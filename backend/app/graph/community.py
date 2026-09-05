import networkx as nx
from typing import Dict, List, Any, Set
import time
from app.graph.engine import graph_engine

def detect_fraud_communities(min_cluster_size: int = 3, min_user_count: int = 2) -> List[Dict[str, Any]]:
    """
    Scans the global transaction graph for dense, suspicious connected components
    representing coordinated abuse rings and Sybil networks.
    """
    with graph_engine._lock:
        g = graph_engine._graph
        if g.number_of_nodes() == 0:
            return []

        # Find connected components on entity-identifier subgraph (excluding merchant mega-hubs)
        non_merchant_nodes = [n for n in g.nodes() if not n.startswith("merchant:")]
        entity_subgraph = g.subgraph(non_merchant_nodes)
        components = list(nx.connected_components(entity_subgraph))
        suspicious_clusters = []

        for idx, comp in enumerate(components):
            if len(comp) < min_cluster_size:
                continue

            subg = g.subgraph(comp)
            users = [n for n in comp if g.nodes[n].get("type") == "user"]
            devices = [n for n in comp if g.nodes[n].get("type") == "device"]
            ips = [n for n in comp if g.nodes[n].get("type") == "ip"]
            cards = [n for n in comp if g.nodes[n].get("type") == "payment_method"]
            merchants = [n for n in comp if g.nodes[n].get("type") == "merchant"]

            if len(users) < min_user_count:
                continue

            # Calculate cluster risk metrics
            user_to_device = len(users) / max(len(devices), 1)
            user_to_ip = len(users) / max(len(ips), 1)
            user_to_card = len(users) / max(len(cards), 1)
            density = nx.density(subg) if len(comp) > 1 else 0.0

            # Heuristic Risk Score for the syndicate
            # High user count sharing few devices/cards = extreme risk
            risk_score = 0.0
            signals = []

            if user_to_device >= 3.0:
                risk_score += 0.35
                signals.append(f"High Device Sharing: {len(users)} users share {len(devices)} devices")
            elif user_to_device >= 1.5:
                risk_score += 0.15
                signals.append(f"Moderate Device Sharing: {len(users)} users share {len(devices)} devices")

            if user_to_ip >= 4.0:
                risk_score += 0.25
                signals.append(f"IP Concentration: {len(users)} accounts from {len(ips)} IPs")

            if user_to_card >= 2.0:
                risk_score += 0.30
                signals.append(f"Card Pooling: {len(users)} accounts share {len(cards)} payment cards")

            if density >= 0.2 and len(comp) >= 5:
                risk_score += 0.20
                signals.append(f"High Graph Density ({round(density, 3)}) indicating tight collusion")

            risk_score = min(round(risk_score, 3), 1.0)

            # Check if any member in this cluster is already quarantined
            is_quarantined = any(n in graph_engine._quarantined_nodes for n in comp)

            if risk_score >= 0.40:
                cluster_id = f"ring_{idx+1}_{int(time.time())}"
                suspicious_clusters.append({
                    "cluster_id": cluster_id,
                    "risk_score": risk_score,
                    "severity": "CRITICAL" if risk_score >= 0.75 else "HIGH" if risk_score >= 0.55 else "MEDIUM",
                    "total_nodes": len(comp),
                    "user_count": len(users),
                    "device_count": len(devices),
                    "ip_count": len(ips),
                    "card_count": len(cards),
                    "density": round(density, 4),
                    "node_ids": list(comp),
                    "signals": signals,
                    "is_quarantined": is_quarantined,
                    "detected_at": time.time()
                })

        # Sort clusters by risk score descending
        suspicious_clusters.sort(key=lambda c: c["risk_score"], reverse=True)
        return suspicious_clusters
