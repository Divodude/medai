"""
Session and history CRUD routes.
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel

from db.database import get_db
from db import crud

router = APIRouter()


class DietLogRequest(BaseModel):
    session_id: str
    meal_name: str


class ExerciseLogRequest(BaseModel):
    session_id: str
    exercise_name: str
    completed: bool = True


@router.get("/sessions")
def list_sessions(db: DBSession = Depends(get_db)):
    sessions = crud.get_all_sessions(db)
    return [
        {
            "id": s.id,
            "patient_name": s.patient_name,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]


@router.get("/history/{session_id}")
def get_session_history(session_id: str, db: DBSession = Depends(get_db)):
    analyses = crud.get_analyses_for_session(db, session_id)
    diet_logs = crud.get_diet_logs(db, session_id)
    exercise_logs = crud.get_exercise_logs(db, session_id)
    doctors = crud.get_doctor_results(db, session_id)

    return {
        "session_id": session_id,
        "analyses": [
            {
                "id": a.id,
                "created_at": a.created_at.isoformat(),
                "condition": a.condition,
                "severity": a.severity,
                "summary": a.summary,
                "key_findings": json.loads(a.key_findings or "[]"),
                "specialty": a.specialty,
                "diet_plan": json.loads(a.diet_plan or "[]"),
                "exercise_plan": json.loads(a.exercise_plan or "[]"),
                "home_remedies": json.loads(a.home_remedies or "[]"),
            }
            for a in analyses
        ],
        "diet_logs": [
            {"meal_name": d.meal_name, "logged_at": d.logged_at.isoformat()}
            for d in diet_logs
        ],
        "exercise_logs": [
            {
                "exercise_name": e.exercise_name,
                "completed": e.completed,
                "logged_at": e.logged_at.isoformat(),
            }
            for e in exercise_logs
        ],
        "doctors": [
            {
                "name": d.name,
                "specialty": d.specialty,
                "address": d.address,
                "phone": d.phone,
                "rating": d.rating,
                "maps_link": d.maps_link,
            }
            for d in doctors
        ],
    }


@router.post("/log/diet")
def log_diet(req: DietLogRequest, db: DBSession = Depends(get_db)):
    crud.get_or_create_session(db, req.session_id)
    entry = crud.log_diet(db, req.session_id, req.meal_name)
    return {"status": "logged", "meal_name": entry.meal_name}


@router.post("/log/exercise")
def log_exercise(req: ExerciseLogRequest, db: DBSession = Depends(get_db)):
    crud.get_or_create_session(db, req.session_id)
    entry = crud.log_exercise(db, req.session_id, req.exercise_name, req.completed)
    return {"status": "logged", "exercise_name": entry.exercise_name, "completed": entry.completed}
