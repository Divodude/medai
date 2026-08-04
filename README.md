# 🏥 AI Health Assistant & Clinical Document ETL Pipeline

An advanced end-to-end medical document intelligence system built with **FastAPI, React, LangGraph, ChromaDB, and Groq Llama-3**. 
Unlike traditional wraps around LLM APIs, this project integrates a robust, auditable **Data Engineering ETL Pipeline** engineered for enterprise resilience, structured data extraction, and semantic Retrieval-Augmented Generation (RAG).

---

## 🏛️ Data Engineering & ETL Pipeline Architecture

The document ingestion engine is architected as a dedicated, decoupled data pipeline (`backend/etl_pipeline/`) enforcing strict **Extract-Transform-Load (ETL)** separation of concerns:

```
┌─────────────────────────┐
│ Raw Document Upload     │ (PDF, Medical Image, or Text Report)
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 1. EXTRACT STAGE        │ ➔ Lazy-loaded multi-pass voting EasyOCR for images
│ (etl_pipeline/extract.py)│ ➔ PyMuPDF stream extraction for clinical PDFs
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 2. TRANSFORM STAGE      │ ➔ Recursive Character Text Splitting (Chunking)
│(etl_pipeline/transform) │ ➔ LLM Function Calling (Pydantic health profiles)
│                         │ ➔ Automated Schema Syntax Recovery Engine
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 3. LOAD STAGE           │ ➔ Dense Vector Indexing in ChromaDB (for RAG Chat)
│  (etl_pipeline/load.py) │ ➔ Relational Storage in SQLite (for Dashboard & History)
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ AUDIT & OBSERVABILITY   │ ➔ PipelineRun audit tracking & state transition logging
│   (db/models & logs)    │    (STARTED ➔ EXTRACTING ➔ TRANSFORMING ➔ LOADING ➔ COMPLETED)
└─────────────────────────┘
```

### 🔥 Key Data Engineering Highlights
* **Decoupled Ingestion Engine:** REST API controllers contain no business or ML logic; they delegate execution to a resilient ETL orchestrator with automated logging and state rotation (`backend/logs/etl_pipeline.log`).
* **Automated Schema Recovery & Fault Tolerance:** Large Language Models (e.g., Llama-3 on Groq) occasionally emit syntax anomalies during tool calling (wrapping JSON in tokens like `<function=Model> {...}`). Our TRANSFORM layer implements a custom **balanced-brace extraction algorithm** (`_recover_json_from_error`) that intercepts malformed generations, extracts valid JSON payloads, validates schemas against Pydantic models, and succeeds without failing production ETL runs.
* **Full Pipeline Audit Tracking:** Every ingestion job creates a historical audit record in SQLite (`PipelineRun` schema). Execution status transitions, processing durations, error traces, and record counts can be inspected via dedicated API endpoints (`/pipeline-runs/{session_id}`).
* **Lazy OCR Initialization:** Heavy vision ML packages (`easyocr`, `opencv-python`, `numpy`) are lazily initialized only when an image is ingested, ensuring high-performance API startups and lightweight executions for plain text/PDF tasks.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key in `.env` (`GROQ_API_KEY=your_api_key_here`)

### 1. Install Backend Dependencies
```powershell
cd E:\Learning\GenAi\my_doc_ai
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### 2. Run API & ETL Pipeline Unit Tests
To verify all ETL components, vector store indexing, schema recovery, and endpoint routing:
```powershell
cd E:\Learning\GenAi\my_doc_ai\backend
..\venv\Scripts\python.exe -m unittest test_api.py -v
```

### 3. Start Backend Server (FastAPI + ETL Engine)
```powershell
# ⚠️ Run from project ROOT directory
cd E:\Learning\GenAi\my_doc_ai
.\venv\Scripts\Activate.ps1
uvicorn backend.api.main:app --reload --port 8000
```

- **Interactive API Documentation (Swagger UI):** http://localhost:8000/docs
- **Pipeline Run Audit Endpoint Example:** http://localhost:8000/pipeline-runs/your_session_id

### 4. Start Frontend Application (React + Vite + Zustand)
```powershell
cd E:\Learning\GenAi\my_doc_ai\frontend
npm install
npm run dev
```
- **Web App Dashboard:** http://localhost:5173

---

## 📂 Project Structure

```
my_doc_ai/
├── .env                     ← Environment configuration (GROQ_API_KEY)
├── backend/
│   ├── etl_pipeline/        ← ⭐ Dedicated Data Engineering ETL Pipeline Module
│   │   ├── __init__.py      ← Pipeline Orchestrator & State Tracking
│   │   ├── extract.py       ← Multi-modal text extraction (PDF / EasyOCR)
│   │   ├── transform.py     ← Chunking, LLM extraction & schema recovery engine
│   │   ├── load.py          ← ChromaDB vector store & SQLite loader
│   │   ├── models.py        ← PipelineRun audit log schema
│   │   └── logger.py        ← Centralized rotating log handler
│   ├── api/
│   │   ├── main.py          ← FastAPI server setup & audit routing
│   │   └── routes/          ← Thin REST endpoint controllers (analyze, chat, doctors)
│   ├── graph/               ← LangGraph multi-turn RAG conversation engine
│   ├── db/                  ← SQLAlchemy database models and CRUD queries
│   ├── tools/               ← DuckDuckGo real-time nearby cardiologist/doctor search
│   ├── logs/                ← Rotated execution system logs (.gitignore excluded)
│   ├── test_api.py          ← End-to-end automated unit test runner
│   └── requirements.txt     ← Project Python dependencies
└── frontend/
    ├── src/
    │   ├── components/      ← Interactive cards (Diet, Exercise, Remedy, Doctor, UploadZone)
    │   ├── pages/           ← Patient Health Dashboard & Session History
    │   ├── store/           ← Zustand application state store
    │   └── api/             ← Axios asynchronous HTTP client
    └── package.json
```

---

## ✨ Application Features

- 🩺 **Automated Clinical ETL:** Upload complex diagnostic reports (PDFs, lab pictures, reports) for automated structured transformation and database ingestion.
- 💬 **Semantic RAG Assistant:** Chat interactively about your diagnostic indicators with full conversational context retrieved from dense embeddings in ChromaDB.
- 🥗 **Personalized Diet Plan Cards:** Nutritional recommendations targeting identified conditions and abnormalities.
- 🏋️ **Trackable Exercise & Lifestyle Routines:** Physical activity guidance adjusted for clinical symptoms and physical limitations.
- 🌿 **Curated Safe Home Remedies:** Evidence-aligned remedy preparations and lifestyle guidance.
- 👨‍⚕️ **Geolocated Specialist Referrals:** Automatic DuckDuckGo search integration locating specialized nearby physicians when severe health conditions are classified.
- 📊 **Historical Audit Trails:** Comprehensive diagnostic session archives and verifiable ETL execution logs.
