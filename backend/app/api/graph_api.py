from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.graph.engine import graph_engine
from app.graph.community import detect_fraud_communities
from app.agent.actions import action_engine

router = APIRouter(prefix="/graph", tags=["Graph Intelligence"])

class QuarantineNodeRequest(BaseModel):
    node_id: str
    reason: str = "Manual Quarantine via SOC Console"

class QuarantineClusterRequest(BaseModel):
    cluster_id: str
    node_ids: List[str]
    reason: str = "Sybil Ring Isolation"

@router.get("/overview")
async def get_graph_overview(max_nodes: int = 300):
    """
    Returns full graph serialized for Cytoscape/Vis.js visualization.
    """
    return graph_engine.get_full_graph_serialized(max_nodes=max_nodes)

@router.get("/ego/{node_id}")
async def get_ego_subgraph(node_id: str, radius: int = 2):
    """
    Returns localized ego-subgraph for a specific node.
    """
    return graph_engine.get_ego_subgraph(node_id, radius=radius)

@router.get("/syndicates")
async def get_detected_syndicates(min_cluster_size: int = 3):
    """
    Scans the graph and returns all detected fraud rings & communities.
    """
    return detect_fraud_communities(min_cluster_size=min_cluster_size)

@router.post("/quarantine/node")
async def quarantine_single_node(payload: QuarantineNodeRequest):
    """
    Quarantines a specific node.
    """
    result = action_engine.execute_quarantine(
        node_id=payload.node_id,
        reason=payload.reason,
        agent_confidence=1.0
    )
    return result

@router.post("/quarantine/cluster")
async def quarantine_fraud_cluster(payload: QuarantineClusterRequest):
    """
    Quarantines an entire detected fraud syndicate.
    """
    result = action_engine.execute_cluster_isolation(
        cluster_id=payload.cluster_id,
        node_ids=payload.node_ids,
        reason=payload.reason,
        agent_confidence=1.0
    )
    return result

@router.post("/reset")
async def reset_graph_state():
    """
    Resets the graph and quarantine registries.
    """
    graph_engine.clear()
    return {"status": "cleared"}
