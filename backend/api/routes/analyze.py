"""
POST /analyze — Upload medical report (PDF, text, image), run ingestion, return health cards.
"""
import uuid
import json
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from db.database import get_db
from db import crud
from rag.ingestion import ingest_document
from llm_provider import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

router = APIRouter()

class LabValue(BaseModel):
    marker: str
    value: str
    unit: str

class StructuredHealthProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    diagnoses: List[str] = Field(default_factory=list)
    abnormal_lab_values: List[LabValue] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    deficiencies: List[str] = Field(default_factory=list)

class HealthAnalysisOutput(BaseModel):
    condition: str = Field(description="The primary medical condition identified")
    severity: str = Field(description="Severity of the condition: LOW, MEDIUM, or HIGH")
    summary: str = Field(description="A concise summary of the report")
    key_findings: List[str] = Field(description="A list of key medical findings")
    specialty: str = Field(description="The recommended medical specialty to consult (e.g., Cardiologist)")
    diet_plan: List[str] = Field(description="A list of recommended dietary changes")
    exercise_plan: List[str] = Field(description="A list of recommended exercises or lifestyle changes")
    home_remedies: List[str] = Field(description="A list of safe home remedies")

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
    if not session_id:
        session_id = str(uuid.uuid4())

    crud.get_or_create_session(db, session_id, patient_name)

    file_bytes = await file.read()
    mime = file.content_type or "application/octet-stream"
    
   
    try:
        full_text = ingest_document(file_bytes, file.filename, mime, session_id)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": f"Ingestion failed: {exc}"})
    
 
    llm = get_llm(temperature=0.0)
    profile_llm = llm.with_structured_output(StructuredHealthProfile)
    
    char_limit = 20000
    merged_profile = None
    
    if len(full_text) > char_limit:
        chunks = [full_text[i:i+char_limit] for i in range(0, len(full_text), char_limit)]
        profiles = []
        for chunk in chunks:
            try:
                p = profile_llm.invoke([
                    SystemMessage(content="Extract health profile from this chunk of medical text."),
                    HumanMessage(content=chunk)
                ])
                profiles.append(p)
            except Exception:
                continue
                
        try:
            merged_profile = profile_llm.invoke([
                SystemMessage(content="Merge these partial health profiles into a single deduplicated profile."),
                HumanMessage(content=json.dumps([p.model_dump() for p in profiles]))
            ])
        except Exception:
            merged_profile = StructuredHealthProfile()
    else:
        try:
            merged_profile = profile_llm.invoke([
                SystemMessage(content="You are an expert clinical data extractor. Extract a comprehensive structured profile."),
                HumanMessage(content=full_text)
            ])
        except Exception:
            merged_profile = StructuredHealthProfile()

    # 3. Generate structured analysis using LLM based on holistic profile
    rec_llm = llm.with_structured_output(HealthAnalysisOutput)
    
    system_prompt = (
        "You are an expert AI medical assistant. "
        "Based on the provided holistic patient Structured Health Profile, generate "
        "condition, severity, summary, key findings, specialty, diet plan, exercise plan, and home remedies. "
        "CRITICAL RULE: Account for allergies and physical limitations."
    )
    
    try:
        analysis: HealthAnalysisOutput = rec_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Health Profile:\n\n{merged_profile.model_dump_json()}")
        ])
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": f"LLM Analysis failed: {exc}"})

    # Convert to dict for DB and response
    result_dict = analysis.model_dump()
    result_dict["structured_summary"] = merged_profile.model_dump_json()
    
    # 3. Persist analysis to DB
    crud.save_analysis(db, session_id, result_dict)

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
            "nearby_doctors": [], # Doctor search can be invoked via chat later or we could do it here
            "error": None,
        }
    )
