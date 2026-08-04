"""
FastAPI application entry point.
"""
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession

from db.database import Base, engine, get_db
from db import models  # noqa: F401 — ensure models are registered
from db import crud
from etl_pipeline import models as pipeline_models  # noqa: F401 — register PipelineRun model
from api.routes import analyze, sessions, chat, doctors

# This is the Database Creation Command and it is run when the server starts
Base.metadata.create_all(bind=engine)


# Now we have initialised the fast api Object
app = FastAPI(
    title="AI Health Assistant",
    description="Smart AI doctor assistant powered by LangGraph + Groq Vision",
    version="1.0.0",
)

# Added the middleware in the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the routers in the main app
app.include_router(analyze.router, tags=["Analysis"])
app.include_router(sessions.router, tags=["Sessions"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(doctors.router, tags=["Doctors"])


# Default endpoint for checking the health of the server
@app.get("/")
def healthcheck():
    return {"status": "ok", "service": "AI Health Assistant API"}


# ─── Pipeline Runs endpoint ─────────────────────────────────────────────────

@app.get("/pipeline-runs/{session_id}", tags=["Pipeline"])
def get_pipeline_runs(
    session_id: str,
    db: DBSession = Depends(get_db),
):
    """
    Get ETL pipeline run history for a given session.
    Useful for monitoring pipeline status and debugging failures.
    """
    runs = crud.get_pipeline_runs(db, session_id)
    return {
        "session_id": session_id,
        "pipeline_runs": [
            {
                "id": r.id,
                "filename": r.filename,
                "status": r.status,
                "error_message": r.error_message,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "records_loaded": r.records_loaded,
            }
            for r in runs
        ],
    }
