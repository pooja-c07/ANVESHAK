# ANVESHAK (SIH26189)
## AI-Powered Criminal Network Analysis & Intelligence Decision Support System
**Smart India Hackathon (SIH 2026) Working Prototype**

---

### 🚨 Mandatory Legal & Ethical Guardrail
> **INVESTIGATIVE DECISION SUPPORT ONLY — NOT LEGAL PROOF OF GUILT**  
> Outputs produced by ANVESHAK are probabilistic investigative leads to assist law enforcement officers (Special Cell, State Police, NIA, CBI, ED). All electronic intelligence, call detail records (CDRs), and financial trails require forensic corroboration and formal certification under **Section 63 of the Bharatiya Sakshya Adhiniyam (BSA), 2023** (formerly Section 65B of the Indian Evidence Act) prior to judicial proceedings.

---

### 🌐 Key Features & Capabilities

1. **Multilingual Investigation Text Ingestion**:
   - Ingests raw case diaries, FIRs, interrogation transcripts, and telecom intercepts in **English, Devanagari Hindi, and Transliterated Hinglish**.
   - Modular architecture ready for **AI4Bharat IndicNER, IndicBERT, and IndicTrans2**.

2. **Automated Entity Extraction**:
   - `PERSON`: Indian names, transliterations, aliases (*Vikram Singhania, Deepak Verma, Sameer Khan, Rocky*).
   - `ACCOUNT`: Bank accounts, IFSC codes, UPI mule accounts (*HDFC-MULE-4819, AXIS-SHELL-9032*).
   - `LOCATION`: Indian districts, transit hubs, and international Hawala nodes (*Jamtara, Surat, Karol Bagh, Dubai*).
   - `PHONE`: Indian cellular & burner numbers (+91-XXXXX-XXXXX, IMEI tower clusters).
   - `DATE`: Indian standard dates, relative Hindi dates (*दिनांक 14 फरवरी 2026, 12 January 2026*).
   - `AMOUNT`: Indian numbering notations (*₹75,00,000, 75 Lakhs, ₹1.85 Crores*).

3. **Relationship Mapping**:
   - `CALL`: Directional CDR call records, frequency, duration.
   - `CONTACT`: Syndicate meetings, encrypted chat handles.
   - `TRANSFER`: Financial laundering routes, IMPS/RTGS/Hawala transactions.
   - `OWNS`: Device ownership, bank account signatories.
   - `VISITED`: Safehouse locations, travel departures.

4. **Dynamic Cyber Knowledge Graph**:
   - Vis.js interactive network canvas with customized node icons, risk-level styling, directional arrows, and physics simulation.
   - **Dynamic Ingestion**: When new investigation text is processed, the graph automatically injects new suspect nodes, links them to existing syndicates, and highlights changes in real-time.
   - Centrality & Hub Analysis: Degree centrality ranking, high-risk node identification.
   - Search & Filters: Real-time fuzzy search and entity/relationship toggles.

5. **Temporal Timeline Slider**:
   - Scrub through time (January to February 2026) to visualize chronological criminal network evolution and event sequences.
   - Play/Pause automated timeline reconstruction.

6. **Explainable Lead & Evidence Panel**:
   - Click any node or link to view exact source sentence provenance, confidence scores, extraction reasoning, and connected suspects.

7. **SHA-256 Evidence Chain-of-Custody & Tamper Verifier**:
   - Every piece of text is cryptographically hashed with SHA-256 upon ingestion.
   - Interactive Tamper Verifier tests text integrity and immediately sounds an alert if even a single character has been modified.

---

### 🚀 Quick Start Instructions

#### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

#### 2. Run the Server
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Or simply:
```bash
python backend/main.py
```

#### 3. Open the Cyber Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

### 🧪 Running Automated Tests
To run the automated verification suite:
```bash
python tests/test_pipeline.py
```

---

### 📂 Project Structure
```
anveshak/
├── backend/
│   ├── graph/
│   │   └── engine.py             # Dynamic in-memory graph engine & centrality metrics
│   ├── nlp/
│   │   ├── base.py               # Data models & BaseNLPExtractor interface
│   │   ├── extractor.py          # Multilingual extraction engine (English, Hindi, Hinglish)
│   │   └── indic_adapter.py      # IndicNER, IndicBERT, IndicTrans2 adapter stubs
│   ├── security/
│   │   └── evidence_verifier.py  # SHA-256 chain-of-custody & tamper detection
│   ├── load_data.py              # Synthetic case loader
│   ├── main.py                   # FastAPI REST API & static file server
│   └── requirements.txt          # Python dependencies
├── data/
│   └── synthetic_cases.json      # Realistic Indian cybercrime and Hawala syndicates
├── frontend/
│   └── index.html                # Dark cyber investigator dashboard (Vis.js + Tailwind)
├── tests/
│   └── test_pipeline.py          # Comprehensive automated test suite
├── docker-compose.yml            # Container definitions
└── README.md                     # Project documentation
```
