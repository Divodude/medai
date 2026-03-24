# AI Health Assistant — Quick Start

## Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key in `.env`

## 1. Install Backend Dependencies
```powershell
cd E:\Learning\GenAi\my_doc_ai
pip install -r backend/requirements.txt
```

## 2. Run Backend (FastAPI)
```powershell
# ⚠️ Must run from project ROOT (not the backend folder)
cd E:\Learning\GenAi\my_doc_ai
.\venv\Scripts\Activate.ps1
uvicorn backend.api.main:app --reload --port 8000
```
API docs available at: http://localhost:8000/docs

## 3. Install & Run Frontend (React + Vite)
```powershell
cd E:\Learning\GenAi\my_doc_ai\frontend
npm install
npm run dev
```
Frontend available at: http://localhost:5173

## Project Structure
```
my_doc_ai/
├── .env                     ← GROQ_API_KEY here
├── backend/
│   ├── api/main.py          ← FastAPI entry point
│   ├── api/routes/          ← analyze, sessions, chat, doctors
│   ├── graph/               ← LangGraph pipeline (6 nodes)
│   ├── db/                  ← SQLite (models, crud, database)
│   ├── tools/               ← DuckDuckGo doctor search
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/      ← DietCard, ExerciseCard, RemedyCard, DoctorCard, UploadZone, ChatSidebar, ProgressRing
    │   ├── pages/           ← Dashboard, History
    │   ├── store/           ← Zustand global state
    │   └── api/             ← Axios client
    └── package.json
```

## Features
- 🩺 **Medical Report Analysis** — Upload any report image (Groq Llama 4 Scout Vision)
- 🥗 **Diet Plan Cards** — 5 personalised meal cards with macros & logging
- 🏋️ **Exercise Cards** — Trackable exercises with difficulty badges
- 🌿 **Home Remedies** — Ingredient-based remedy cards with step-by-step guides
- 👨‍⚕️ **Nearby Doctors** — DuckDuckGo search with GPS location (auto on HIGH severity)
- 💬 **AI Chat** — Streaming follow-up chat with full report context
- 📊 **Health History** — SQLite-backed session history with stats
