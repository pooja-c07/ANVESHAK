"""
ANVESHAK - AI-Powered Criminal Network Analysis System
Base NLP interfaces, data contracts, and evidentiary models.
Compliant with Bharatiya Sakshya Adhiniyam (BSA) / Indian Evidence Act guidelines:
All AI outputs are investigative leads, NOT proof of guilt.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


EntityType = Literal["PERSON", "ACCOUNT", "LOCATION", "PHONE", "DATE", "AMOUNT"]
RelationshipType = Literal["CALL", "CONTACT", "TRANSFER", "OWNS", "VISITED"]


class TextEvidenceSpan(BaseModel):
    start_char: int
    end_char: int
    text: str
    context_sentence: str


class ExtractedEntity(BaseModel):
    id: str
    name: str
    type: EntityType
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_span: Optional[TextEvidenceSpan] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"


class ExtractedRelationship(BaseModel):
    id: str
    source_entity_id: str
    source_label: str
    target_entity_id: str
    target_label: str
    type: RelationshipType
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_text: str
    timestamp: Optional[str] = None
    why_detected: Optional[str] = "Correlated via contextual entity extraction and investigative heuristics"
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    text_length: int
    language_detected: str
    sha256_hash: str
    timestamp: str
    entities: List[ExtractedEntity]
    relationships: List[ExtractedRelationship]
    disclaimer: str = (
        "AI-ASSISTED INVESTIGATIVE LEAD ONLY — NOT PROOF OF GUILT — "
        "SUBJECT TO FORENSIC VERIFICATION UNDER BHARATIYA SAKSHYA ADHINIYAM (BSA)"
    )


class BaseNLPExtractor(ABC):
    """Abstract interface for modular NLP backends (Rule-based, IndicNER, IndicBERT, etc.)"""

    @abstractmethod
    def extract(self, text: str, **kwargs) -> ExtractionResult:
        """Extract entities and relationships from raw investigative text."""
        pass
