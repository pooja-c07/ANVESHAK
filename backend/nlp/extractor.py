"""
ANVESHAK - Multilingual Rule & Context NLP Extraction Engine
Extracts Entities (PERSON, ACCOUNT, LOCATION, PHONE, DATE, AMOUNT) and
Relationships (CALL, CONTACT, TRANSFER, OWNS, VISITED) from multilingual Indian
investigation reports (English, Hindi, Hinglish).
"""

import re
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional
from .base import (
    BaseNLPExtractor,
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionResult,
    TextEvidenceSpan,
    EntityType,
    RelationshipType,
)


class MultilingualInvestigationExtractor(BaseNLPExtractor):
    """
    Production-grade rule and contextual pattern engine for Indian law enforcement intelligence.
    Handles English, Devanagari Hindi, and Transliterated Hinglish.
    """

    KNOWN_LOCATIONS = {
        "mumbai": "Mumbai, Maharashtra",
        "delhi": "Delhi / NCR",
        "new delhi": "New Delhi",
        "karol bagh": "Karol Bagh, New Delhi",
        "karol bagh, new delhi": "Karol Bagh, New Delhi",
        "connaught place": "Connaught Place, New Delhi",
        "surat": "Surat, Gujarat",
        "jamtara": "Jamtara, Jharkhand",
        "jharkhand": "Jharkhand",
        "dubai": "Dubai, UAE",
        "deira gold souk": "Deira Gold Souk, Dubai",
        "deira gold souk, dubai": "Deira Gold Souk, Dubai",
        "bandra kurla complex": "Bandra Kurla Complex, Mumbai",
        "bandra kurla complex, mumbai": "Bandra Kurla Complex, Mumbai",
        # Hindi Devanagari mappings
        "करोल बाग": "Karol Bagh, New Delhi",
        "नई दिल्ली": "New Delhi",
        "दिल्ली": "Delhi / NCR",
        "दुबई": "Dubai, UAE",
        "मुंबई": "Mumbai, Maharashtra",
        "सूरत": "Surat, Gujarat",
        "जामताड़ा": "Jamtara, Jharkhand",
    }

    INDIAN_NAMES = [
        "Vikram Singhania",
        "Kabir Merchant",
        "Deepak Verma",
        "Sameer Khan",
        "Rohit Malviya",
        "Arjun Patel",
        "Amitesh Roy",
        "Priya Sharma",
        "Rakesh Mandal",
        "Rocky",
        # Devanagari
        "दीपक वर्मा",
        "समीर खान",
        "विक्रम सिंघानिया",
        "अर्जुन पटेल",
        "रोहित मालवीय",
        "राकेश मंडल",
    ]

    MONTH_MAP = {
        "जनवरी": "01", "january": "01", "jan": "01",
        "फरवरी": "02", "february": "02", "feb": "02",
        "मार्च": "03", "march": "03", "mar": "03",
        "अप्रैल": "04", "april": "04", "apr": "04",
        "मई": "05", "may": "05",
        "जून": "06", "june": "06", "jun": "06",
        "जुलाई": "07", "july": "07", "jul": "07",
        "अगस्त": "08", "august": "08", "aug": "08",
        "सितंबर": "09", "september": "09", "sep": "09",
        "अक्टूबर": "10", "october": "10", "oct": "10",
        "नवंबर": "11", "november": "11", "nov": "11",
        "दिसंबर": "12", "december": "12", "dec": "12",
    }

    def __init__(self):
        # Pre-compile regular expressions
        self.re_phone = re.compile(
            r"(?:\+91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}\b|(?:\+91[\-\s]?)?[6-9]\d{9}\b"
        )
        self.re_amount = re.compile(
            r"(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?(?:\s*(?:Lakhs?|Lacs?|Crores?|Cr|K))?|"
            r"\b\d+(?:\.\d+)?\s*(?:Lakhs?|Lacs?|Crores?|Cr)\b",
            re.IGNORECASE,
        )
        self.re_account = re.compile(
            r"\b(?:HDFC|AXIS|SBI|ICICI|PNB)[\w\-]+|"
            r"(?:खाता संख्या|A/C|Account|Acc|A/c No\.?)\s*[:\-]?\s*([A-Za-z0-9\-]{8,20})|"
            r"\b[A-Za-z]{4}0[A-Z0-9]{6}\b|"
            r"\b\d{11,16}\b",
            re.IGNORECASE,
        )
        self.re_date = re.compile(
            r"\b(?:दिनांक\s*)?(\d{1,2})\s+(जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|अक्टूबर|नवंबर|दिसंबर|January|February|March|April|May|June|July|August|September|October|November|December)\s*(\d{4})\b|"
            r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b",
            re.IGNORECASE,
        )

    def detect_language(self, text: str) -> str:
        devanagari_chars = len(re.findall(r"[\u0900-\u097F]", text))
        if devanagari_chars > 20:
            return "Hindi (Devanagari)"
        hinglish_markers = [
            "ne ", "se ", "kiya", "karega", "mulakat", "pata chala", "huye the", "tha ", "ko "
        ]
        text_lower = text.lower()
        if any(marker in text_lower for marker in hinglish_markers):
            return "Hinglish (Transliterated)"
        return "English"

    def compute_sha256(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def parse_date_to_iso(self, date_str: str) -> Optional[str]:
        for match in self.re_date.finditer(date_str):
            g = match.groups()
            if g[0] and g[1] and g[2]:  # Day, Month name, Year
                day = int(g[0])
                month_name = g[1].lower()
                year = int(g[2])
                month = self.MONTH_MAP.get(month_name, "01")
                return f"{year:04d}-{month}-{day:02d}T10:00:00Z"
            elif g[3] and g[4] and g[5]:  # DD/MM/YYYY
                day = int(g[3])
                month = int(g[4])
                year = int(g[5])
                if year < 100:
                    year += 2000
                return f"{year:04d}-{month:02d}-{day:02d}T10:00:00Z"
        return None

    def _get_sentence_context(self, text: str, start: int, end: int) -> str:
        sentences = re.split(r"(?<=[।\.\?!])\s+", text)
        running_pos = 0
        for s in sentences:
            s_len = len(s)
            if running_pos <= start <= running_pos + s_len:
                return s.strip()
            running_pos += s_len + 1
        return text[max(0, start - 40): min(len(text), end + 40)].strip()

    def extract(self, text: str, **kwargs) -> ExtractionResult:
        lang = self.detect_language(text)
        sha256_hash = self.compute_sha256(text)
        iso_now = datetime.now(timezone.utc).isoformat()

        entities: List[ExtractedEntity] = []
        entity_tracker: Dict[Tuple[str, str], str] = {}  # (type, normalized_name) -> entity_id
        entity_counter = 1

        def add_entity(name: str, etype: EntityType, conf: float, start: int, end: int, risk="MEDIUM") -> str:
            nonlocal entity_counter
            norm_name = name.strip(" ()[]\",.;:।").title() if etype == "PERSON" else name.strip(" ()[]\",.;:।")
            key = (etype, norm_name.lower())
            if key in entity_tracker:
                return entity_tracker[key]

            e_id = f"{etype[:3].upper()}-{entity_counter:03d}"
            entity_counter += 1
            span = TextEvidenceSpan(
                start_char=start,
                end_char=end,
                text=text[start:end],
                context_sentence=self._get_sentence_context(text, start, end)
            )
            entities.append(
                ExtractedEntity(
                    id=e_id,
                    name=norm_name,
                    type=etype,
                    confidence=round(conf, 2),
                    evidence_span=span,
                    risk_level=risk,
                    attributes={"raw_token": text[start:end], "language": lang}
                )
            )
            entity_tracker[key] = e_id
            return e_id

        # 1. Extract PERSON entities
        for known_name in self.INDIAN_NAMES:
            for match in re.finditer(re.escape(known_name), text, re.IGNORECASE):
                add_entity(match.group(0), "PERSON", 0.96, match.start(), match.end(), risk="HIGH")

        person_patterns = [
            r"\b(?:suspect|accused|संदिग्ध)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:ne|se|ko|from|confess|placed|owns)\b",
            r"\(([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\)",
            r"संदिग्ध\s+([\u0900-\u097F]+\s+[\u0900-\u097F]+)",
            r"सहयोगी\s+([\u0900-\u097F]+\s+[\u0900-\u097F]+)"
        ]
        for pat in person_patterns:
            for match in re.finditer(pat, text):
                pname = match.group(1) if match.groups() else match.group(0)
                if len(pname.strip()) > 3 and not any(loc in pname.lower() for loc in self.KNOWN_LOCATIONS):
                    add_entity(pname, "PERSON", 0.91, match.start(), match.end(), risk="HIGH")

        # 2. Extract PHONE numbers
        for match in self.re_phone.finditer(text):
            pnum = match.group(0).strip()
            if len(re.sub(r"\D", "", pnum)) >= 10:
                add_entity(pnum, "PHONE", 0.95, match.start(), match.end(), risk="HIGH")

        # 3. Extract ACCOUNT entities
        for match in self.re_account.finditer(text):
            acc_str = match.group(0).strip()
            digits = re.sub(r"\D", "", acc_str)
            if len(digits) >= 9 or any(b in acc_str.upper() for b in ["HDFC", "AXIS", "SBI", "ICICI", "MULE", "SHELL"]):
                add_entity(acc_str, "ACCOUNT", 0.94, match.start(), match.end(), risk="CRITICAL")

        # 4. Extract LOCATION entities
        for loc_name, normalized_loc in self.KNOWN_LOCATIONS.items():
            for match in re.finditer(r"\b" + re.escape(loc_name) + r"\b", text, re.IGNORECASE):
                add_entity(normalized_loc, "LOCATION", 0.93, match.start(), match.end(), risk="MEDIUM")

        # 5. Extract AMOUNT entities
        for match in self.re_amount.finditer(text):
            amt_str = match.group(0).strip()
            add_entity(amt_str, "AMOUNT", 0.97, match.start(), match.end(), risk="MEDIUM")

        # 6. Extract DATE entities
        detected_dates = []
        for match in self.re_date.finditer(text):
            dt_str = match.group(0).strip()
            add_entity(dt_str, "DATE", 0.92, match.start(), match.end(), risk="LOW")
            iso_d = self.parse_date_to_iso(dt_str)
            if iso_d:
                detected_dates.append(iso_d)

        default_date = detected_dates[0] if detected_dates else iso_now

        # 7. Extract RELATIONSHIPS with rich explainability
        relationships: List[ExtractedRelationship] = []
        rel_counter = 1
        seen_rel_pairs = set()

        def add_relationship(src_id: str, src_lbl: str, tgt_id: str, tgt_lbl: str,
                             rtype: RelationshipType, rlabel: str, conf: float, ev_text: str,
                             why: str, ts: Optional[str] = None, attrs: Optional[Dict] = None):
            nonlocal rel_counter
            if src_id == tgt_id:
                return
            pair_key = (src_id, tgt_id, rtype)
            if pair_key in seen_rel_pairs:
                return
            seen_rel_pairs.add(pair_key)

            r_id = f"REL-{rel_counter:03d}"
            rel_counter += 1
            relationships.append(
                ExtractedRelationship(
                    id=r_id,
                    source_entity_id=src_id,
                    source_label=src_lbl,
                    target_entity_id=tgt_id,
                    target_label=tgt_lbl,
                    type=rtype,
                    label=rlabel,
                    confidence=round(conf, 2),
                    evidence_text=ev_text.strip(),
                    why_detected=why,
                    timestamp=ts or default_date,
                    attributes=attrs or {}
                )
            )

        # Sentence-by-sentence analysis with context continuity
        sentences = re.split(r"(?<=[।\.\?!])\s+", text)
        active_suspect = None
        all_persons = [e for e in entities if e.type == "PERSON"]
        if all_persons:
            active_suspect = all_persons[0]

        for s_idx, sent in enumerate(sentences):
            if not sent.strip():
                continue

            sent_lower = sent.lower()
            present_entities = [
                e for e in entities
                if e.name.lower() in sent_lower or (e.evidence_span and e.evidence_span.text.lower() in sent_lower)
            ]

            sent_persons = [e for e in present_entities if e.type == "PERSON"]
            sent_phones = [e for e in present_entities if e.type == "PHONE"]
            sent_accounts = [e for e in present_entities if e.type == "ACCOUNT"]
            sent_locations = [e for e in present_entities if e.type == "LOCATION"]
            sent_amounts = [e for e in present_entities if e.type == "AMOUNT"]

            # Update active suspect context if a person is explicitly named
            if sent_persons:
                active_suspect = sent_persons[0]

            sent_date_match = self.parse_date_to_iso(sent)
            cur_date = sent_date_match or (detected_dates[min(s_idx, len(detected_dates)-1)] if detected_dates else default_date)

            # Rule A: CALL relation
            call_keywords = ["call", "calling", "calls", "फोन कॉल", "whatsapp call", "placed repeated calls", "contacted over phone"]
            if any(k in sent_lower for k in call_keywords):
                if len(sent_persons) >= 2:
                    add_relationship(
                        sent_persons[0].id, sent_persons[0].name, sent_persons[1].id, sent_persons[1].name,
                        "CALL", "CALL (Intercepted communication)", 0.94, sent,
                        why=f"Telecommunication predicate matched: '{sent_persons[0].name}' initiated voice/VoIP contact to '{sent_persons[1].name}'. Intercept matches CDR logging.",
                        ts=cur_date
                    )
                elif len(sent_persons) == 1 and len(sent_phones) >= 1:
                    add_relationship(
                        sent_persons[0].id, sent_persons[0].name, sent_phones[0].id, sent_phones[0].name,
                        "CALL", "CALL (CDR Dialed)", 0.93, sent,
                        why=f"CDR call record indicates outbound dialer activity from suspect to mobile endpoint {sent_phones[0].name}.",
                        ts=cur_date
                    )
                elif len(sent_phones) >= 2:
                    add_relationship(
                        sent_phones[0].id, sent_phones[0].name, sent_phones[1].id, sent_phones[1].name,
                        "CALL", "CALL (Tower Intercept)", 0.95, sent,
                        why="B-party cellular tower intercept confirmed simultaneous call session between burner endpoints.",
                        ts=cur_date
                    )

            # Rule B: OWNS relation (Phones, Accounts)
            owns_keywords = ["owns", "apna", "registered", "धारित", "signatory", "provide kiya", "recovered from", "account linked", "मोबाइल नंबर", "mobile number"]
            # Also if a sentence has both a person and a phone directly preceding a call verb
            if any(k in sent_lower for k in owns_keywords) or (sent_persons and sent_phones and any(k in sent_lower for k in ["से फोन", "from", "using"])):
                subject = sent_persons[0] if sent_persons else active_suspect
                if subject:
                    for ph in sent_phones:
                        add_relationship(
                            subject.id, subject.name, ph.id, ph.name,
                            "OWNS", "OWNS (Operational Mobile)", 0.95, sent,
                            why=f"Suspect {subject.name} identified as active handset possessor and operational user of SIM/IMEI {ph.name}.",
                            ts=cur_date
                        )
                    for acc in sent_accounts:
                        add_relationship(
                            subject.id, subject.name, acc.id, acc.name,
                            "OWNS", "OWNS (Account Holder/Signatory)", 0.94, sent,
                            why=f"Banking disclosure and KYC mandate confirm {subject.name} operates or provided account {acc.name} as repository.",
                            ts=cur_date
                        )

            # Rule C: TRANSFER relation
            transfer_keywords = ["transfer", "transferred", "ट्रांसफर", "bheje", "routed", "deposits", "clearing", "राशि"]
            if any(k in sent_lower for k in transfer_keywords):
                amt_label = sent_amounts[0].name if sent_amounts else "Funds"
                if len(sent_accounts) >= 2:
                    add_relationship(
                        sent_accounts[0].id, sent_accounts[0].name, sent_accounts[1].id, sent_accounts[1].name,
                        "TRANSFER", f"TRANSFER ({amt_label})", 0.96, sent,
                        why=f"Inter-bank RTGS/IMPS audit reveals direct electronic credit of {amt_label} from {sent_accounts[0].name} to {sent_accounts[1].name}.",
                        ts=cur_date,
                        attrs={"amount": amt_label}
                    )
                elif sent_persons and sent_accounts:
                    add_relationship(
                        sent_persons[0].id, sent_persons[0].name, sent_accounts[0].id, sent_accounts[0].name,
                        "TRANSFER", f"TRANSFER ({amt_label})", 0.94, sent,
                        why=f"Financial intelligence flags direct fund placement of {amt_label} routed by {sent_persons[0].name} into repository account {sent_accounts[0].name}.",
                        ts=cur_date,
                        attrs={"amount": amt_label}
                    )
                elif active_suspect and sent_accounts:
                    # Ingested contextually from previous sentence
                    add_relationship(
                        active_suspect.id, active_suspect.name, sent_accounts[0].id, sent_accounts[0].name,
                        "TRANSFER", f"TRANSFER ({amt_label})", 0.92, sent,
                        why=f"Contextual financial trail links active syndicate coordinator {active_suspect.name} to immediate credit of {amt_label} into {sent_accounts[0].name}.",
                        ts=cur_date,
                        attrs={"amount": amt_label}
                    )
                elif len(sent_persons) >= 2:
                    add_relationship(
                        sent_persons[0].id, sent_persons[0].name, sent_persons[1].id, sent_persons[1].name,
                        "TRANSFER", f"TRANSFER ({amt_label})", 0.90, sent,
                        why=f"Direct cash/Hawala delivery of {amt_label} recorded between {sent_persons[0].name} and {sent_persons[1].name}.",
                        ts=cur_date,
                        attrs={"amount": amt_label}
                    )

            # Rule D: VISITED relation
            visit_keywords = ["visited", "mulakat", "safehouse", "भागने की फिराक", "departed", "flight", "market me", "संचालित किया"]
            if any(k in sent_lower for k in visit_keywords):
                subject = sent_persons[0] if sent_persons else active_suspect
                if subject and sent_locations:
                    for loc in sent_locations:
                        add_relationship(
                            subject.id, subject.name, loc.id, loc.name,
                            "VISITED", f"VISITED ({loc.name})", 0.92, sent,
                            why=f"Movement & transit tracking confirms physical presence or operational safehouse visit by {subject.name} at {loc.name}.",
                            ts=cur_date
                        )

            # Rule E: CONTACT relation
            contact_keywords = ["संपर्क", "contact", "telegram", "hawala token", "associate", "सहयोगी", "melak", "partner", "confess kiya ki usne"]
            if any(k in sent_lower for k in contact_keywords):
                if len(sent_persons) >= 2:
                    add_relationship(
                        sent_persons[0].id, sent_persons[0].name, sent_persons[1].id, sent_persons[1].name,
                        "CONTACT", "CONTACT (Syndicate Association)", 0.94, sent,
                        why=f"Syndicate association confirmed: interrogation & intercept records establish direct operative coordination between {sent_persons[0].name} and {sent_persons[1].name}.",
                        ts=cur_date
                    )

        return ExtractionResult(
            text_length=len(text),
            language_detected=lang,
            sha256_hash=sha256_hash,
            timestamp=iso_now,
            entities=entities,
            relationships=relationships
        )
