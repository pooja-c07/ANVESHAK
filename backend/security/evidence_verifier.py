"""
ANVESHAK - SHA-256 Chain of Custody & Evidence Verification Subsystem
Provides tamper detection, digital hashing, and audit seal certificates
compliant with Bharatiya Sakshya Adhiniyam (BSA) digital forensics requirements.
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict, Any


class EvidenceVerifier:
    """Cryptographic hash engine for chain-of-custody assurance."""

    @staticmethod
    def compute_sha256(text: str) -> str:
        clean = text.strip()
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()

    @classmethod
    def verify_integrity(cls, current_text: str, registered_hash: str) -> Dict[str, Any]:
        computed_hash = cls.compute_sha256(current_text)
        is_authentic = (computed_hash.lower() == registered_hash.strip().lower())

        return {
            "is_authentic": is_authentic,
            "status": "VERIFIED_AUTHENTIC" if is_authentic else "TAMPERED_BREACH_DETECTED",
            "algorithm": "SHA-256",
            "registered_hash": registered_hash.strip().lower(),
            "computed_hash": computed_hash,
            "char_count": len(current_text),
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "forensic_status_message": (
                "MATCH: Evidence integrity preserved. Cryptographic hash matches official ledger."
                if is_authentic
                else "ALERT: Integrity breach! Text content has been altered or manipulated since initial registration."
            ),
        }

    @classmethod
    def create_custody_seal(cls, text: str, investigator_id: str = "OFFICER-748", case_id: str = "CASE-2026-CHHAYA") -> Dict[str, Any]:
        computed_hash = cls.compute_sha256(text)
        iso_time = datetime.now(timezone.utc).isoformat()
        seal_token = f"BSA-SEC-{case_id}-{computed_hash[:16].upper()}"

        return {
            "seal_token": seal_token,
            "case_id": case_id,
            "investigator_id": investigator_id,
            "sha256_hash": computed_hash,
            "algorithm": "SHA-256",
            "timestamp": iso_time,
            "standards_compliance": "Bharatiya Sakshya Adhiniyam (BSA) Sec 63 / Digital Evidence Chain-of-Custody",
            "status": "SEALED",
        }
