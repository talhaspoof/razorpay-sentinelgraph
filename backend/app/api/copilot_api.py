from fastapi import APIRouter
from typing import Dict, Any, List
from pydantic import BaseModel
import json
from app.graph.engine import graph_engine
from app.graph.community import detect_fraud_communities
from app.core.config import settings

router = APIRouter(prefix="/copilot", tags=["Threat Hunting Co-Pilot"])

class CopilotQueryRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_with_copilot(payload: CopilotQueryRequest):
    """
    Natural language interface for querying graph intelligence,
    investigating specific entities, and summarizing active threats.
    """
    query = payload.query.lower().strip()
    
    # Extract current graph facts
    syndicates = detect_fraud_communities()
    serialized = graph_engine.get_full_graph_serialized(max_nodes=100)
    total_nodes = serialized.get("total_nodes", 0)
    total_edges = serialized.get("total_edges", 0)
    quarantined_count = len(graph_engine._quarantined_nodes)
    
    # Try LLM if available
    llm_answer = None
    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = f"""
            You are Sentinel Co-Pilot, an AI risk analyst.
            Current State:
            - Total Graph Nodes: {total_nodes}
            - Total Edges: {total_edges}
            - Quarantined Nodes: {quarantined_count}
            - Active Detected Syndicates: {len(syndicates)}
            - Syndicates Summary: {json.dumps(syndicates[:3])}
            
            User Question: "{payload.query}"
            Provide a concise, professional, insightful answer based on the real data.
            """
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            llm_answer = res.text.strip()
        except Exception:
            pass

    if not llm_answer:
        # Fallback intelligent rule-based response
        if "syndicate" in query or "ring" in query or "cluster" in query:
            if syndicates:
                top = syndicates[0]
                llm_answer = (
                    f"Found **{len(syndicates)} suspicious syndicates** in the active graph. "
                    f"The highest-severity ring is **{top['cluster_id']}** (Risk: {int(top['risk_score']*100)}%, Severity: {top['severity']}) "
                    f"with {top['user_count']} users sharing {top['device_count']} devices and {top['card_count']} cards. "
                    f"Primary signals: {', '.join(top['signals'])}."
                )
            else:
                llm_answer = "No suspicious fraud syndicates detected in the current transaction stream. Graph topology is within normal variance."
        elif "quarantine" in query or "blocked" in query:
            llm_answer = (
                f"There are currently **{quarantined_count} quarantined entities** in the isolation registry. "
                "Any incoming transaction from these nodes is automatically halted or challenged."
            )
        elif "status" in query or "overview" in query or "summary" in query:
            llm_answer = (
                f"**SentinelGraph Status**: Ingesting live transactions. Tracking {total_nodes} entity nodes across {total_edges} edges. "
                f"Identified {len(syndicates)} active threat clusters. {quarantined_count} entities quarantined."
            )
        else:
            llm_answer = (
                f"Analyzed query: *'{payload.query}'*. Graph currently holds {total_nodes} nodes and {len(syndicates)} detected fraud rings. "
                "You can ask me to explain specific syndicates, check quarantined nodes, or look up device and IP concentrations."
            )

    return {
        "query": payload.query,
        "response": llm_answer,
        "context": {
            "total_nodes": total_nodes,
            "syndicates_count": len(syndicates),
            "quarantined_count": quarantined_count
        }
    }
