import json
from datetime import datetime
from sqlalchemy.orm import Session as DBSession
from backend.db.models import Session, AnalysisResult, DietLog, ExerciseLog, DoctorResult


# ─── Session ────────────────────────────────────────────────────────────────

def get_or_create_session(db: DBSession, session_id: str, patient_name: str = "Patient") -> Session:
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        session = Session(id=session_id, patient_name=patient_name)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def get_all_sessions(db: DBSession):
    return db.query(Session).order_by(Session.created_at.desc()).all()


# ─── Analysis ────────────────────────────────────────────────────────────────

def save_analysis(db: DBSession, session_id: str, data: dict) -> AnalysisResult:
    result = AnalysisResult(
        session_id=session_id,
        condition=data.get("condition"),
        severity=data.get("severity", "LOW"),
        summary=data.get("summary"),
        key_findings=json.dumps(data.get("key_findings", [])),
        specialty=data.get("specialty"),
        diet_plan=json.dumps(data.get("diet_plan", [])),
        exercise_plan=json.dumps(data.get("exercise_plan", [])),
        home_remedies=json.dumps(data.get("home_remedies", [])),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_analyses_for_session(db: DBSession, session_id: str):
    return (
        db.query(AnalysisResult)
        .filter(AnalysisResult.session_id == session_id)
        .order_by(AnalysisResult.created_at.desc())
        .all()
    )


# ─── Diet Log ────────────────────────────────────────────────────────────────

def log_diet(db: DBSession, session_id: str, meal_name: str) -> DietLog:
    entry = DietLog(session_id=session_id, meal_name=meal_name)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_diet_logs(db: DBSession, session_id: str):
    return db.query(DietLog).filter(DietLog.session_id == session_id).all()


# ─── Exercise Log ────────────────────────────────────────────────────────────

def log_exercise(db: DBSession, session_id: str, exercise_name: str, completed: bool = True) -> ExerciseLog:
    entry = ExerciseLog(session_id=session_id, exercise_name=exercise_name, completed=completed)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_exercise_logs(db: DBSession, session_id: str):
    return db.query(ExerciseLog).filter(ExerciseLog.session_id == session_id).all()


# ─── Doctor Results ───────────────────────────────────────────────────────────

def save_doctor_results(db: DBSession, session_id: str, doctors: list) -> list:
    saved = []
    for d in doctors:
        dr = DoctorResult(
            session_id=session_id,
            name=d.get("name"),
            specialty=d.get("specialty"),
            address=d.get("address"),
            phone=d.get("phone"),
            rating=d.get("rating"),
            maps_link=d.get("maps_link"),
        )
        db.add(dr)
        saved.append(dr)
    db.commit()
    return saved


def get_doctor_results(db: DBSession, session_id: str):
    return db.query(DoctorResult).filter(DoctorResult.session_id == session_id).all()
