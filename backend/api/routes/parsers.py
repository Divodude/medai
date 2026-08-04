from typing import List, Optional
from pydantic import BaseModel, Field


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
