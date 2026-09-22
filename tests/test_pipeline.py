"""
ANVESHAK - Comprehensive Automated Pipeline Tests
Tests multilingual entity & relation extraction, dynamic graph updates,
and SHA-256 evidence verification.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.nlp.extractor import MultilingualInvestigationExtractor
from backend.graph.engine import NetworkGraphEngine
from backend.security.evidence_verifier import EvidenceVerifier
from backend.load_data import get_case_by_id, get_sample_texts


def test_multilingual_extraction():
    print("\n--- TEST 1: Multilingual NLP Extraction ---")
    extractor = MultilingualInvestigationExtractor()
    samples = get_sample_texts()

    for s in samples:
        res = extractor.extract(s["text"])
        print(f"\n[Language: {res.language_detected}] Sample: '{s['title']}'")
        print(f"  SHA-256 Hash: {res.sha256_hash[:16]}...")
        print(f"  Entities Extracted ({len(res.entities)}):")
        types_found = set()
        for ent in res.entities:
            types_found.add(ent.type)
            print(f"    - [{ent.type}] {ent.name} (Conf: {ent.confidence*100:.0f}%, Risk: {ent.risk_level})")

        print(f"  Relationships Extracted ({len(res.relationships)}):")
        for rel in res.relationships:
            print(f"    - ({rel.source_label}) --[{rel.label}]--> ({rel.target_label}) [Conf: {rel.confidence*100:.0f}%]")

        # Assertions
        assert len(res.entities) > 0, f"No entities extracted for {s['id']}"
        assert len(res.relationships) > 0, f"No relationships extracted for {s['id']}"
        assert "PERSON" in types_found, "PERSON entity must be detected"

    print(">>> Test 1 Passed: Multilingual extraction verified successfully.")


def test_dynamic_graph_engine():
    print("\n--- TEST 2: Dynamic Graph Engine & Centrality ---")
    engine = NetworkGraphEngine()
    case = get_case_by_id("CASE-2026-CHHAYA")
    engine.load_case_data(case)

    initial_nodes = len(engine.nodes)
    initial_edges = len(engine.edges)
    print(f"Initial Graph: {initial_nodes} nodes, {initial_edges} edges.")

    # Extract new intelligence from Hindi sample
    extractor = MultilingualInvestigationExtractor()
    sample_hi = get_sample_texts()[0]
    extraction = extractor.extract(sample_hi["text"])

    # Ingest into graph
    stats = engine.ingest_extraction(extraction, source_title="Hindi FIR Special Cell")
    print(f"Ingestion Stats: {stats}")

    assert engine.get_node_by_name("Deepak Verma") is not None, "Deepak Verma should be present in graph"
    assert len(engine.nodes) > initial_nodes, "Nodes count must increase dynamically"
    assert len(engine.edges) > initial_edges, "Edges count must increase dynamically"

    # Verify metrics
    metrics = engine.compute_metrics()
    print(f"Top Centrality Hubs: {metrics['top_hubs']}")
    assert len(metrics["top_hubs"]) > 0, "Top hubs must be identified"

    # Verify timeline
    timeline = engine.get_timeline()
    print(f"Temporal Timeline Events: {len(timeline)}")
    assert len(timeline) >= len(engine.edges), "Timeline events must match edge history"

    print(">>> Test 2 Passed: Dynamic graph ingestion & metrics verified.")


def test_sha256_verification_and_tamper_detection():
    print("\n--- TEST 3: SHA-256 Tamper Detection & BSA Custody Seal ---")
    original_text = "Suspect Rohit Malviya transferred ₹25,00,000 to safehouse account on 12 January 2026."
    registered_hash = EvidenceVerifier.compute_sha256(original_text)

    # 1. Authentic check
    check_ok = EvidenceVerifier.verify_integrity(original_text, registered_hash)
    print(f"Authentic Check Status: {check_ok['status']}")
    assert check_ok["is_authentic"] is True
    assert check_ok["status"] == "VERIFIED_AUTHENTIC"

    # 2. Tampered check (single character change: 25 Lakhs -> 35 Lakhs)
    tampered_text = "Suspect Rohit Malviya transferred ₹35,00,000 to safehouse account on 12 January 2026."
    check_tampered = EvidenceVerifier.verify_integrity(tampered_text, registered_hash)
    print(f"Tampered Check Status: {check_tampered['status']}")
    assert check_tampered["is_authentic"] is False
    assert check_tampered["status"] == "TAMPERED_BREACH_DETECTED"

    # 3. Seal generation
    seal = EvidenceVerifier.create_custody_seal(original_text, investigator_id="OFFICER-748")
    print(f"Custody Seal Generated: {seal['seal_token']} (Algorithm: {seal['algorithm']})")
    assert "BSA-SEC" in seal["seal_token"]

    print(">>> Test 3 Passed: SHA-256 tamper detection and custody seal verified.")


if __name__ == "__main__":
    print("==========================================================")
    print("       ANVESHAK (SIH26189) PIPELINE VERIFICATION         ")
    print("==========================================================")
    test_multilingual_extraction()
    test_dynamic_graph_engine()
    test_sha256_verification_and_tamper_detection()
    print("\n==========================================================")
    print("       ALL BACKEND & ALGORITHMIC TESTS PASSED!            ")
    print("==========================================================")
