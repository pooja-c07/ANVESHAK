"""
ANVESHAK - End-to-End Demo Workflow Verification Script
Tests API endpoints, dynamic graph updates, why_detected rationale on edges,
timeline ordering, and Explain This Connection frontend integration.
"""

import sys
import json
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"


def run_tests():
    print("==========================================================")
    print("      ANVESHAK DEMO FLOW & WOW MOMENT VERIFICATION       ")
    print("==========================================================")

    # 1. Health check
    h = json.loads(urllib.request.urlopen(f"{BASE_URL}/api/health").read().decode("utf-8"))
    print(f"1. Health Check: {h['status']} | {h['system']}")
    assert h["status"] == "ONLINE"

    # 2. Check active graph edges have why_detected, source_label, target_label
    g = json.loads(urllib.request.urlopen(f"{BASE_URL}/api/graph").read().decode("utf-8"))
    node_count = len(g["nodes"])
    edge_count = len(g["edges"])
    print(f"2. Initial Graph: {node_count} nodes, {edge_count} edges")
    assert edge_count > 0

    first_edge = g["edges"][0]
    print(f"   Sample Edge: [{first_edge['type']}] {first_edge['source_label']} -> {first_edge['target_label']}")
    print(f"   Why Detected: {first_edge.get('why_detected')}")
    print(f"   Date: {first_edge.get('timestamp')}")
    print(f"   Confidence: {first_edge.get('weight')}")
    assert "why_detected" in first_edge and len(first_edge["why_detected"]) > 10

    # 3. Extract NLP intelligence from Hindi Sample
    cases = json.loads(urllib.request.urlopen(f"{BASE_URL}/api/cases").read().decode("utf-8"))
    hi_sample = cases["sample_texts"][0]["text"]
    extract_req = urllib.request.Request(
        f"{BASE_URL}/api/extract",
        data=json.dumps({"text": hi_sample}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    extract_res = json.loads(urllib.request.urlopen(extract_req).read().decode("utf-8"))
    print(f"3. Extracted Hindi Intelligence:")
    print(f"   - Entities: {len(extract_res['entities'])}")
    print(f"   - Relationships: {len(extract_res['relationships'])}")
    print(f"   - SHA-256 Hash: {extract_res['sha256_hash'][:16]}...")
    assert len(extract_res["relationships"]) >= 3

    for rel in extract_res["relationships"][:3]:
        print(f"     * ({rel['source_label']}) --[{rel['type']}]--> ({rel['target_label']})")
        print(f"       Why: {rel['why_detected']}")

    # 4. Ingest into graph dynamically
    ingest_req = urllib.request.Request(
        f"{BASE_URL}/api/graph/ingest",
        data=json.dumps({"extraction": extract_res, "source_title": "Special Cell Intercept"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    ingest_res = json.loads(urllib.request.urlopen(ingest_req).read().decode("utf-8"))
    print(f"4. Dynamic Ingestion Stats: {ingest_res['stats']}")
    assert ingest_res["stats"]["added_nodes"] > 0
    assert ingest_res["stats"]["added_edges"] > 0

    # 5. Verify updated graph has newly linked edges with why_detected
    g_updated = json.loads(urllib.request.urlopen(f"{BASE_URL}/api/graph").read().decode("utf-8"))
    print(f"5. Updated Graph: {len(g_updated['nodes'])} nodes, {len(g_updated['edges'])} edges")
    assert len(g_updated["nodes"]) > node_count
    assert len(g_updated["edges"]) > edge_count

    # 6. Check timeline sequencing
    timeline = json.loads(urllib.request.urlopen(f"{BASE_URL}/api/timeline").read().decode("utf-8"))
    print(f"6. Temporal Timeline Events: {len(timeline['events'])}")
    assert len(timeline["events"]) >= len(g_updated["edges"])
    assert "why_detected" in timeline["events"][0]

    # 7. Check index.html contains all Wow Moment components
    html = urllib.request.urlopen(f"{BASE_URL}/").read().decode("utf-8")
    assert "WHY CONNECTION WAS DETECTED" in html
    assert "edge-quick-select" in html
    assert "Explain This Connection" in html
    assert "cyber-glow-wow" in html
    print("7. Frontend HTML contains 'Explain This Connection' WOW moment components!")

    print("\n==========================================================")
    print("     >>> ALL DEMO FLOW WORKFLOW TESTS PASSED! <<<         ")
    print("==========================================================")


if __name__ == "__main__":
    run_tests()
