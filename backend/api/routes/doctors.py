"""
GET /doctors — On-demand doctor search with DuckDuckGo.
"""
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session as DBSession

from backend.db.database import get_db
from backend.db import crud
from backend.tools.doctor_search import search_doctors

router = APIRouter()


@router.get("/doctors")
def get_nearby_doctors(
    specialty: str = Query(..., description="Medical specialty, e.g. cardiologist"),
    city: str = Query(default="", description="City name derived from GPS coords"),
    session_id: str = Query(default=None),
    db: DBSession = Depends(get_db),
):
    doctors = search_doctors(specialty=specialty, city=city)

    # Persist if session provided
    if session_id and doctors:
        crud.get_or_create_session(db, session_id)
        crud.save_doctor_results(db, session_id, doctors)

    return {"doctors": doctors}
