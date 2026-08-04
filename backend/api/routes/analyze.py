"""
POST /analyze — Upload medical report (PDF, text, image), run ETL pipeline, return health cards.

This endpoint acts as a thin API layer: it receives the file, delegates all
processing to the ETL pipeline, and returns the structured response.
"""
import uuid
import json
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DBSession

from db.database import get_db
from db import crud
from etl_pipeline import run_pipeline


# Initialised the router for the analyse file
router = APIRouter()


@router.post("/analyze")
async def analyze_report(
    file: UploadFile = File(...),
    session_id: str = Form(default=None),
    lat: float = Form(default=None),
    lng: float = Form(default=None),
    city: str = Form(default=""),
    patient_name: str = Form(default="Patient"),
    db: DBSession = Depends(get_db),
):
    """
    Upload a medical document and receive AI-powered health analysis.

    The endpoint delegates all processing to the ETL pipeline which:
    1. EXTRACTS text from the uploaded document (PDF/image/text)
    2. TRANSFORMS it into structured knowledge via LLM
    3. LOADS results into ChromaDB (vectors) and SQLite (analysis)
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    crud.get_or_create_session(db, session_id, patient_name)

    file_bytes = await file.read()
    mime = file.content_type or "application/octet-stream"

    # ── Run the ETL Pipeline ─────────────────────────────────────────
    try:
        result_dict = run_pipeline(file_bytes, file.filename, mime, session_id, db)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"error": f"Pipeline failed: {exc}"},
        )

    # ── Return structured response ───────────────────────────────────
    return JSONResponse(
        content={
            "session_id": session_id,
            "condition": result_dict["condition"],
            "severity": result_dict["severity"],
            "summary": result_dict["summary"],
            "key_findings": result_dict["key_findings"],
            "specialty": result_dict["specialty"],
            "structured_summary": json.loads(result_dict["structured_summary"]),
            "diet_plan": result_dict["diet_plan"],
            "exercise_plan": result_dict["exercise_plan"],
            "home_remedies": result_dict["home_remedies"],
            "nearby_doctors": [],
            "error": None,
        }
    )
