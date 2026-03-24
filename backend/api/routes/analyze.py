"""
POST /analyze — Upload medical report image, run LangGraph pipeline, return health cards.
"""
import base64
import json
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DBSession

from db.database import get_db
from db import crud
from graph.builder import health_graph

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
    # Generate session_id if not provided
    if not session_id:
        session_id = str(uuid.uuid4())

    # Ensure session exists in DB
    crud.get_or_create_session(db, session_id, patient_name)

    # Read image and convert to base64 data URL
    image_bytes = await file.read()
    mime = file.content_type or "image/jpeg"
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:{mime};base64,{b64}"

    # Build initial graph state
    initial_state = {
        "session_id": session_id,
        "image_b64": image_data_url,
        "location": {"lat": lat, "lng": lng, "city": city},
        "messages": [],
        "condition": None,
        "severity": None,
        "summary": None,
        "key_findings": None,
        "specialty": None,
        "diet_plan": None,
        "exercise_plan": None,
        "home_remedies": None,
        "nearby_doctors": None,
        "error": None,
    }

    # Run the LangGraph pipeline
    result = await health_graph.ainvoke(initial_state)

    # Persist analysis to DB
    crud.save_analysis(db, session_id, result)

    if result.get("nearby_doctors"):
        crud.save_doctor_results(db, session_id, result["nearby_doctors"])

    return JSONResponse(
        content={
            "session_id": session_id,
            "condition": result.get("condition"),
            "severity": result.get("severity"),
            "summary": result.get("summary"),
            "key_findings": result.get("key_findings", []),
            "specialty": result.get("specialty"),
            "diet_plan": result.get("diet_plan", []),
            "exercise_plan": result.get("exercise_plan", []),
            "home_remedies": result.get("home_remedies", []),
            "nearby_doctors": result.get("nearby_doctors", []),
            "error": result.get("error"),
        }
    )
