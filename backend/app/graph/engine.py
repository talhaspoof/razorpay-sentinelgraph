import networkx as nx
from typing import Dict, List, Any, Optional, Set, Tuple
import threading
import time

class SentinelGraphEngine:
    """
    In-memory, real-time graph intelligence engine for transaction entity linking
    and localized ego-subgraph extraction.
    """
    def __init__(self):
        self._graph = nx.MultiGraph()
        self._lock = threading.RLock()
        self._quarantined_nodes: Set[str] = set()
        self._quarantined_clusters: Dict[str, Dict[str, Any]] = {}
        self._transaction_history: List[Dict[str, Any]] = []

    def clear(self):
        with self._lock:
            self._graph.clear()
            self._quarantined_nodes.clear()
            self._quarantined_clusters.clear()
            self._transaction_history.clear()

    def add_transaction(self, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests a payment transaction payload, links entities as nodes & edges,
        and returns the extracted localized 2-hop ego subgraph.
        """
        with self._lock:
            tx_id = tx_payload.get("id") or f"pay_{int(time.time()*1000)}"
            user_id = tx_payload.get("user_id", "anon_user")
            device_id = tx_payload.get("device_fingerprint", "unknown_device")
            ip_address = tx_payload.get("ip_address", "127.0.0.1")
            card_hash = tx_payload.get("card_token") or tx_payload.get("vpa") or "unknown_payment_instrument"
            shipping_addr = tx_payload.get("shipping_address_hash") or "unknown_address"
            merchant_id = tx_payload.get("merchant_id", "default_merchant")
            amount = float(tx_payload.get("amount", 0.0))
            timestamp = tx_payload.get("timestamp", time.time())
            status = tx_payload.get("status", "authorized")

            # Node Definitions
            user_node = f"user:{user_id}"
            device_node = f"device:{device_id}"
            ip_node = f"ip:{ip_address}"
            card_node = f"payment:{card_hash}"
            addr_node = f"addr:{shipping_addr}"
            merchant_node = f"merchant:{merchant_id}"

            # Add / Update Nodes with metadata
            self._graph.add_node(user_node, type="user", label=user_id, first_seen=timestamp, last_seen=timestamp)
            self._graph.add_node(device_node, type="device", label=device_id[:10] + "...", first_seen=timestamp, last_seen=timestamp)
            self._graph.add_node(ip_node, type="ip", label=ip_address, first_seen=timestamp, last_seen=timestamp)
            self._graph.add_node(card_node, type="payment_method", label=card_hash[:12] + "...", first_seen=timestamp, last_seen=timestamp)
            if shipping_addr != "unknown_address":
                self._graph.add_node(addr_node, type="address", label=shipping_addr[:10] + "...", first_seen=timestamp, last_seen=timestamp)
            self._graph.add_node(merchant_node, type="merchant", label=merchant_id, first_seen=timestamp, last_seen=timestamp)

            # Add Relationship Edges
            edge_attrs = {"tx_id": tx_id, "amount": amount, "timestamp": timestamp, "status": status}
            self._graph.add_edge(user_node, device_node, key=f"used_device_{tx_id}", relation="USED_DEVICE", **edge_attrs)
            self._graph.add_edge(user_node, ip_node, key=f"from_ip_{tx_id}", relation="FROM_IP", **edge_attrs)
            self._graph.add_edge(user_node, card_node, key=f"paid_with_{tx_id}", relation="PAID_WITH", **edge_attrs)
            if shipping_addr != "unknown_address":
                self._graph.add_edge(user_node, addr_node, key=f"shipped_to_{tx_id}", relation="SHIPPED_TO", **edge_attrs)
            self._graph.add_edge(user_node, merchant_node, key=f"transacted_at_{tx_id}", relation="TRANSACTED_AT", **edge_attrs)

            # Record Transaction in linear log
            tx_record = {
                "id": tx_id,
                "user_id": user_id,
                "device_id": device_id,
                "ip_address": ip_address,
                "payment_instrument": card_hash,
                "shipping_address": shipping_addr,
                "merchant_id": merchant_id,
                "amount": amount,
                "timestamp": timestamp,
                "status": status,
                "primary_node": user_node
            }
            self._transaction_history.append(tx_record)

            # Fast 2-Hop Ego Graph Extraction
            ego_subgraph = self.get_ego_subgraph(user_node, radius=2)
            return {
                "transaction": tx_record,
                "ego_subgraph": ego_subgraph
            }

    def get_ego_subgraph(self, center_node: str, radius: int = 2) -> Dict[str, Any]:
        """
        Extracts a localized ego-subgraph centered around a specific node up to `radius` hops.
        Excludes mega-hub nodes (e.g. merchants) from bridging unrelated users.
        Extremely fast (<5ms) for real-time payment gateway latency constraints.
        """
        with self._lock:
            if center_node not in self._graph:
                return {"nodes": [], "edges": [], "metrics": {"node_count": 0, "edge_count": 0, "density": 0.0}}

            # Filter out merchant nodes during BFS path traversal to avoid false-positive mega-hub bridging
            non_hub_nodes = [n for n in self._graph.nodes() if not n.startswith("merchant:")]
            traversal_subgraph = self._graph.subgraph(non_hub_nodes)

            if center_node in traversal_subgraph:
                subgraph_nodes = set(nx.single_source_shortest_path_length(traversal_subgraph, center_node, cutoff=radius).keys())
            else:
                subgraph_nodes = {center_node}

            # Add immediate merchant connections for the center user for context
            for neighbor in self._graph.neighbors(center_node):
                if neighbor.startswith("merchant:"):
                    subgraph_nodes.add(neighbor)

            subgraph = self._graph.subgraph(subgraph_nodes)

            nodes_data = []
            for n in subgraph.nodes():
                node_attrs = dict(self._graph.nodes[n])
                node_attrs["id"] = n
                node_attrs["is_quarantined"] = n in self._quarantined_nodes
                node_attrs["degree"] = self._graph.degree(n)
                nodes_data.append(node_attrs)

            edges_data = []
            for u, v, k, d in subgraph.edges(keys=True, data=True):
                edge_item = dict(d)
                edge_item["id"] = f"{u}->{v}:{k}"
                edge_item["source"] = u
                edge_item["target"] = v
                edges_data.append(edge_item)

            num_nodes = len(nodes_data)
            num_edges = len(edges_data)
            density = nx.density(subgraph) if num_nodes > 1 else 0.0

            return {
                "center_node": center_node,
                "nodes": nodes_data,
                "edges": edges_data,
                "metrics": {
                    "node_count": num_nodes,
                    "edge_count": num_edges,
                    "density": round(density, 4),
                    "user_count": sum(1 for n in nodes_data if n.get("type") == "user"),
                    "device_count": sum(1 for n in nodes_data if n.get("type") == "device"),
                    "ip_count": sum(1 for n in nodes_data if n.get("type") == "ip"),
                    "card_count": sum(1 for n in nodes_data if n.get("type") == "payment_method")
                }
            }

    def get_full_graph_serialized(self, max_nodes: int = 400) -> Dict[str, Any]:
        """
        Returns full graph serialized for Cytoscape/Vis.js visualization.
        """
        with self._lock:
            nodes_data = []
            for n in list(self._graph.nodes())[:max_nodes]:
                node_attrs = dict(self._graph.nodes[n])
                node_attrs["id"] = n
                node_attrs["is_quarantined"] = n in self._quarantined_nodes
                node_attrs["degree"] = self._graph.degree(n)
                nodes_data.append(node_attrs)

            active_node_ids = {n["id"] for n in nodes_data}
            edges_data = []
            for u, v, k, d in self._graph.edges(keys=True, data=True):
                if u in active_node_ids and v in active_node_ids:
                    edge_item = dict(d)
                    edge_item["id"] = f"{u}->{v}:{k}"
                    edge_item["source"] = u
                    edge_item["target"] = v
                    edges_data.append(edge_item)

            return {
                "nodes": nodes_data,
                "edges": edges_data,
                "total_nodes": self._graph.number_of_nodes(),
                "total_edges": self._graph.number_of_edges()
            }

    def quarantine_node(self, node_id: str, reason: str = "") -> bool:
        with self._lock:
            if node_id in self._graph:
                self._quarantined_nodes.add(node_id)
                return True
            return False

    def quarantine_cluster(self, cluster_id: str, node_ids: List[str], reason: str = "") -> Dict[str, Any]:
        with self._lock:
            quarantined = []
            for nid in node_ids:
                if nid in self._graph:
                    self._quarantined_nodes.add(nid)
                    quarantined.append(nid)
            
            cluster_info = {
                "cluster_id": cluster_id,
                "node_ids": quarantined,
                "reason": reason,
                "quarantined_at": time.time()
            }
            self._quarantined_clusters[cluster_id] = cluster_info
            return cluster_info

    def is_quarantined(self, node_id: str) -> bool:
        with self._lock:
            return node_id in self._quarantined_nodes

# Global Singleton Instance
graph_engine = SentinelGraphEngine()
