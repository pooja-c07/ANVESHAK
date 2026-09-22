"""
ANVESHAK - Dynamic In-Memory Criminal Network Graph Engine
Supports dynamic node/edge insertion, deduplication, forensic filtering,
centrality & risk scoring, and temporal event sequencing.
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone
import json
from ..nlp.base import ExtractedEntity, ExtractedRelationship, ExtractionResult


class NetworkGraphEngine:
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, Dict[str, Any]] = {}
        self.active_case_id: str = "CASE-2026-CHHAYA"
        self.case_meta: Dict[str, Any] = {}

    def clear(self):
        self.nodes.clear()
        self.edges.clear()

    def load_case_data(self, case_dict: Dict[str, Any]):
        self.clear()
        self.active_case_id = case_dict.get("id", "UNKNOWN")
        self.case_meta = {
            "id": case_dict.get("id"),
            "title": case_dict.get("title"),
            "description": case_dict.get("description"),
            "lead_officer": case_dict.get("lead_officer"),
            "risk_level": case_dict.get("risk_level"),
            "disclaimer": case_dict.get("disclaimer"),
        }

        for n in case_dict.get("initial_nodes", []):
            self.nodes[n["id"]] = dict(n)

        for e in case_dict.get("initial_edges", []):
            self.edges[e["id"]] = dict(e)

    def get_node_by_name(self, name: str, etype: Optional[str] = None) -> Optional[Dict[str, Any]]:
        name_lower = name.strip().lower()
        for node in self.nodes.values():
            if node.get("label", "").lower() == name_lower:
                if etype is None or node.get("type") == etype:
                    return node
        return None

    def ingest_extraction(self, extraction: ExtractionResult, source_title: str = "Extracted Intelligence") -> Dict[str, Any]:
        """
        Dynamically ingests entities and relationships extracted from NLP into the graph.
        Performs deduplication and link stitching.
        """
        added_nodes = 0
        updated_nodes = 0
        added_edges = 0
        id_mapping: Dict[str, str] = {}  # temporary extraction id -> actual graph node id

        # 1. Ingest or merge entities
        for ent in extraction.entities:
            existing = self.get_node_by_name(ent.name, ent.type)
            if existing:
                graph_node_id = existing["id"]
                # Update confidence or add source
                existing["confidence"] = max(existing.get("confidence", 0.0), ent.confidence)
                if "sources" not in existing:
                    existing["sources"] = [existing.get("source", "Seed Data")]
                if source_title not in existing["sources"]:
                    existing["sources"].append(source_title)
                updated_nodes += 1
            else:
                graph_node_id = f"DYN-{ent.type[:3]}-{len(self.nodes) + 1:03d}"
                node_data = {
                    "id": graph_node_id,
                    "label": ent.name,
                    "type": ent.type,
                    "risk": ent.risk_level,
                    "confidence": ent.confidence,
                    "source": source_title,
                    "sources": [source_title],
                    "hash": extraction.sha256_hash,
                    "extracted_at": extraction.timestamp,
                    "evidence_snippet": ent.evidence_span.context_sentence if ent.evidence_span else None,
                    "attributes": ent.attributes,
                }
                self.nodes[graph_node_id] = node_data
                added_nodes += 1

            id_mapping[ent.id] = graph_node_id
            id_mapping[ent.name.lower()] = graph_node_id

        # 2. Ingest or merge relationships
        for rel in extraction.relationships:
            src_node_id = id_mapping.get(rel.source_entity_id) or id_mapping.get(rel.source_label.lower())
            tgt_node_id = id_mapping.get(rel.target_entity_id) or id_mapping.get(rel.target_label.lower())

            if not src_node_id or not tgt_node_id:
                # Attempt lookup in existing graph
                src_exist = self.get_node_by_name(rel.source_label)
                tgt_exist = self.get_node_by_name(rel.target_label)
                if src_exist:
                    src_node_id = src_exist["id"]
                if tgt_exist:
                    tgt_node_id = tgt_exist["id"]

            if src_node_id and tgt_node_id and src_node_id != tgt_node_id:
                # Check for existing edge between these nodes
                edge_id = f"EDGE-{src_node_id}-{tgt_node_id}-{rel.type}"
                if edge_id in self.edges:
                    self.edges[edge_id]["weight"] = max(self.edges[edge_id].get("weight", 0.5), rel.confidence)
                    self.edges[edge_id]["evidence"] = f"{self.edges[edge_id].get('evidence', '')} | {rel.evidence_text}"
                    if rel.why_detected:
                        self.edges[edge_id]["why_detected"] = rel.why_detected
                else:
                    new_edge_id = f"DYN-E-{len(self.edges) + 1:03d}"
                    self.edges[new_edge_id] = {
                        "id": new_edge_id,
                        "source": src_node_id,
                        "target": tgt_node_id,
                        "type": rel.type,
                        "label": rel.label,
                        "weight": rel.confidence,
                        "timestamp": rel.timestamp or extraction.timestamp,
                        "source_doc": source_title,
                        "evidence": rel.evidence_text,
                        "why_detected": rel.why_detected or "Correlated via contextual entity extraction and investigative heuristics",
                        "hash": extraction.sha256_hash,
                        "attributes": rel.attributes,
                    }
                    added_edges += 1

        return {
            "added_nodes": added_nodes,
            "updated_nodes": updated_nodes,
            "added_edges": added_edges,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
        }

    def compute_metrics(self) -> Dict[str, Any]:
        """Compute degree centrality and detect primary hubs"""
        degree_map: Dict[str, int] = {nid: 0 for nid in self.nodes}
        for e in self.edges.values():
            s, t = e.get("source"), e.get("target")
            if s in degree_map:
                degree_map[s] += 1
            if t in degree_map:
                degree_map[t] += 1

        # Calculate high centrality suspects
        sorted_hubs = sorted(degree_map.items(), key=lambda x: x[1], reverse=True)
        top_hubs = []
        for nid, deg in sorted_hubs[:5]:
            if deg > 0 and nid in self.nodes:
                n = self.nodes[nid]
                top_hubs.append({
                    "id": nid,
                    "label": n.get("label"),
                    "type": n.get("type"),
                    "connections": deg,
                    "risk": n.get("risk", "MEDIUM")
                })

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "degree_map": degree_map,
            "top_hubs": top_hubs,
        }

    def get_graph_data(
        self,
        query: Optional[str] = None,
        entity_types: Optional[List[str]] = None,
        relation_types: Optional[List[str]] = None,
        min_confidence: float = 0.0,
    ) -> Dict[str, Any]:
        """Returns filtered nodes and edges for Vis.js visualization."""
        metrics = self.compute_metrics()
        degree_map = metrics["degree_map"]

        filtered_nodes: List[Dict[str, Any]] = []
        visible_node_ids: Set[str] = set()

        q_lower = query.strip().lower() if query else None

        for nid, node in self.nodes.items():
            # Confidence filter
            if node.get("confidence", 1.0) < min_confidence:
                continue

            # Entity type filter
            if entity_types and node.get("type") not in entity_types:
                continue

            # Search query filter
            if q_lower:
                label = node.get("label", "").lower()
                role = node.get("role", "").lower()
                details = node.get("details", "").lower()
                loc = node.get("location", "").lower()
                if q_lower not in label and q_lower not in role and q_lower not in details and q_lower not in loc:
                    continue

            node_out = dict(node)
            node_out["degree"] = degree_map.get(nid, 0)
            filtered_nodes.append(node_out)
            visible_node_ids.add(nid)

        filtered_edges: List[Dict[str, Any]] = []
        for eid, edge in self.edges.items():
            s, t = edge.get("source"), edge.get("target")
            if s in visible_node_ids and t in visible_node_ids:
                if relation_types and edge.get("type") not in relation_types:
                    continue
                if edge.get("weight", 1.0) < min_confidence:
                    continue
                e_copy = dict(edge)
                src_n = self.nodes.get(s, {})
                tgt_n = self.nodes.get(t, {})
                e_copy["source_label"] = src_n.get("label", s)
                e_copy["target_label"] = tgt_n.get("label", t)
                e_copy["why_detected"] = edge.get("why_detected") or "Identified through multi-source intelligence correlation and investigative pattern analysis."
                filtered_edges.append(e_copy)

        return {
            "case_meta": self.case_meta,
            "nodes": filtered_nodes,
            "edges": filtered_edges,
            "metrics": metrics,
        }

    def get_timeline(self) -> List[Dict[str, Any]]:
        """Returns chronologically sorted list of edge events for timeline tracking."""
        timeline_events = []
        for e in self.edges.values():
            ts = e.get("timestamp") or "2026-01-01T00:00:00Z"
            src_node = self.nodes.get(e.get("source"), {})
            tgt_node = self.nodes.get(e.get("target"), {})
            timeline_events.append({
                "id": e.get("id"),
                "timestamp": ts,
                "type": e.get("type"),
                "label": e.get("label"),
                "source_id": e.get("source"),
                "source_label": src_node.get("label", e.get("source")),
                "target_id": e.get("target"),
                "target_label": tgt_node.get("label", e.get("target")),
                "evidence": e.get("evidence"),
                "why_detected": e.get("why_detected") or "Identified through multi-source intelligence correlation.",
                "source_doc": e.get("source_doc"),
                "weight": e.get("weight", 0.9),
            })

        # Sort chronologically
        timeline_events.sort(key=lambda x: x["timestamp"])
        return timeline_events
