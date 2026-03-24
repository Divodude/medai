"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.database import Base, engine
from backend.db import models  # noqa: F401 — ensure models are registered
from backend.api.routes import analyze, sessions, chat, doctors

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Health Assistant",
    description="Smart AI doctor assistant powered by LangGraph + Groq Vision",
    version="1.0.0",
)

# Allow the React dev server (port 5173) and any local origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(analyze.router, tags=["Analysis"])
app.include_router(sessions.router, tags=["Sessions"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(doctors.router, tags=["Doctors"])


@app.get("/")
def healthcheck():
    return {"status": "ok", "service": "AI Health Assistant API"}
