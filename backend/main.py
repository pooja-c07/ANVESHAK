"""
ANVESHAK — AI-Powered Criminal Network Analysis System (SIH26189)
FastAPI Backend Server providing modular multilingual NLP extraction,
dynamic knowledge graph ingestion, SHA-256 evidence verification,
and cyber forensic dashboard integration.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from backend.nlp.base import ExtractionResult
    from backend.nlp.extractor import MultilingualInvestigationExtractor
    from backend.nlp.indic_adapter import IndicNLPOrchestrator
    from backend.graph.engine import NetworkGraphEngine
    from backend.security.evidence_verifier import EvidenceVerifier
    from backend.load_data import get_all_cases, get_sample_texts, get_case_by_id
else:
    from .nlp.base import ExtractionResult
    from .nlp.extractor import MultilingualInvestigationExtractor
    from .nlp.indic_adapter import IndicNLPOrchestrator
    from .graph.engine import NetworkGraphEngine
    from .security.evidence_verifier import EvidenceVerifier
    from .load_data import get_all_cases, get_sample_texts, get_case_by_id


app = FastAPI(
    title="ANVESHAK Intelligence Engine (SIH26189)",
    description="AI-Assisted Criminal Network Analysis and Dynamic Knowledge Graph System",
    version="1.0.0",
)

# Enable CORS for local development and UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instances
nlp_engine = MultilingualInvestigationExtractor()
graph_engine = NetworkGraphEngine()

# Initialize graph with primary synthetic case
default_case = get_case_by_id("CASE-2026-CHHAYA")
if default_case:
    graph_engine.load_case_data(default_case)


# Request Models
class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Investigation text in English, Hindi, or Hinglish")
    investigator_id: Optional[str] = "INVESTIGATOR-748"
    source_title: Optional[str] = "Field Intelligence Intercept"


class IngestRequest(BaseModel):
    extraction: ExtractionResult
    source_title: Optional[str] = "Extracted Intelligence Intercept"


class VerifyRequest(BaseModel):
    text: str
    registered_hash: str


class CaseSelectRequest(BaseModel):
    case_id: str


# API Endpoints
@app.get("/api/health")
def health_check():
    return {
        "system": "ANVESHAK AI Criminal Network Engine",
        "code": "SIH26189",
        "status": "ONLINE",
        "nlp_backend": "Modular Multilingual Engine (IndicBERT / IndicNER Ready)",
        "security": "SHA-256 Chain-of-Custody Active",
        "compliance": "Bharatiya Sakshya Adhiniyam (BSA) Sec 63 Compliant",
    }


@app.get("/api/cases")
def list_cases():
    cases = get_all_cases()
    samples = get_sample_texts()
    return {
        "cases": [
            {
                "id": c["id"],
                "title": c["title"],
                "description": c["description"],
                "lead_officer": c["lead_officer"],
                "risk_level": c["risk_level"],
                "status": c["status"],
            }
            for c in cases
        ],
        "active_case_id": graph_engine.active_case_id,
        "sample_texts": samples,
    }


@app.post("/api/cases/select")
def select_case(req: CaseSelectRequest):
    case = get_case_by_id(req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    graph_engine.load_case_data(case)
    return {
        "message": f"Loaded case {req.case_id}",
        "active_case_id": graph_engine.active_case_id,
        "metrics": graph_engine.compute_metrics(),
    }


@app.get("/api/graph")
def get_graph(
    q: Optional[str] = Query(None, description="Search term for suspects, accounts, phones"),
    entity_types: Optional[str] = Query(None, description="Comma-separated entity types (PERSON,ACCOUNT,etc.)"),
    relation_types: Optional[str] = Query(None, description="Comma-separated relation types (CALL,TRANSFER,etc.)"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence threshold"),
):
    e_types = [t.strip().upper() for t in entity_types.split(",")] if entity_types else None
    r_types = [t.strip().upper() for t in relation_types.split(",")] if relation_types else None

    return graph_engine.get_graph_data(
        query=q,
        entity_types=e_types,
        relation_types=r_types,
        min_confidence=min_confidence,
    )


@app.post("/api/extract", response_model=ExtractionResult)
def extract_intelligence(req: ExtractRequest):
    """
    Extracts entities (PERSON, ACCOUNT, LOCATION, PHONE, DATE, AMOUNT) and
    relationships (CALL, CONTACT, TRANSFER, OWNS, VISITED) from raw text.
    Computes cryptographic SHA-256 hash for chain-of-custody tracking.
    """
    result = nlp_engine.extract(req.text)
    return result


@app.post("/api/graph/ingest")
def ingest_intelligence(req: IngestRequest):
    """
    Dynamically merges extracted intelligence into the active knowledge graph.
    Updates existing suspect profiles, links burner accounts, and flags new syndicates.
    """
    stats = graph_engine.ingest_extraction(req.extraction, source_title=req.source_title)
    return {
        "status": "SUCCESS",
        "message": "Intelligence successfully linked to knowledge graph",
        "stats": stats,
    }


@app.post("/api/graph/reset")
def reset_graph():
    """Resets the graph to the initial seed state of the active case."""
    case = get_case_by_id(graph_engine.active_case_id)
    if case:
        graph_engine.load_case_data(case)
    return {
        "status": "RESET_SUCCESS",
        "message": "Graph restored to official verified baseline.",
        "metrics": graph_engine.compute_metrics(),
    }


@app.get("/api/timeline")
def get_temporal_timeline():
    """Chronologically sequenced investigative events for timeline visualization."""
    return {
        "case_id": graph_engine.active_case_id,
        "events": graph_engine.get_timeline(),
    }


@app.post("/api/verify")
def verify_evidence(req: VerifyRequest):
    """
    Performs cryptographic SHA-256 verification against the evidence ledger.
    Flags single-character alterations or forensic tampering.
    """
    return EvidenceVerifier.verify_integrity(req.text, req.registered_hash)


@app.post("/api/seal")
def generate_digital_seal(req: ExtractRequest):
    """Generates an evidentiary tamper-evident custody seal under BSA guidelines."""
    return EvidenceVerifier.create_custody_seal(
        req.text,
        investigator_id=req.investigator_id or "OFFICER-748",
        case_id=graph_engine.active_case_id,
    )


# Mount Frontend UI static assets
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "Frontend index.html not yet created."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
