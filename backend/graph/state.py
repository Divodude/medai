from typing import TypedDict, Optional, List, Any


class HealthState(TypedDict):
    """Shared state that flows through the LangGraph pipeline."""
    session_id: str
    image_b64: str                   # base64-encoded report image
    location: Optional[dict]         # {"lat": float, "lng": float, "city": str}

    # Filled by analyze_report_node
    condition: Optional[str]
    severity: Optional[str]          # LOW | MEDIUM | HIGH
    summary: Optional[str]
    key_findings: Optional[List[str]]
    specialty: Optional[str]         # e.g. "cardiologist"

    # Filled by downstream nodes
    diet_plan: Optional[List[dict]]
    exercise_plan: Optional[List[dict]]
    home_remedies: Optional[List[dict]]
    nearby_doctors: Optional[List[dict]]

    # Chat history for context
    messages: List[dict]

    # Error passthrough
    error: Optional[str]
