from typing import List
import json
import re
import logging
from groq import Groq
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.graph.state import HealthState
from backend.tools.doctor_search import search_doctors

logger = logging.getLogger(__name__)
_groq = Groq(api_key=GROQ_API_KEY)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _chat(messages: list, *, max_tokens: int = 2048) -> str:
    """Call Groq chat completions (non-streaming) and return content string."""
    response = _groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.7,
        max_completion_tokens=max_tokens,
        top_p=1,
        stream=False,
    )
    return response.choices[0].message.content or ""


def _extract_json(text: str) -> any:
    """Extract the first JSON block from model output."""
    # Try to find ```json ... ``` block first
    match = re.search(r"```json\s*([\s\S]*?)```", text)
    if match:
        return json.loads(match.group(1))
    # Fall back to raw JSON
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if match:
        return json.loads(match.group(1))
    raise ValueError(f"No JSON found in model output:\n{text[:500]}")


# ─── Node 1: Analyze medical report image ────────────────────────────────────

def analyze_report_node(state: HealthState) -> dict:
    """Use Groq vision to extract structured health data from the report image."""
    try:
        response = _groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are a medical AI assistant analyzing a patient's medical report image. "
                                "Extract the key clinical information and respond ONLY with a valid JSON object "
                                "(no markdown, no explanation) with this exact structure:\n"
                                "{\n"
                                '  "condition": "primary diagnosis or health concern",\n'
                                '  "severity": "LOW|MEDIUM|HIGH",\n'
                                '  "summary": "2-3 sentence plain-language summary for the patient",\n'
                                '  "key_findings": ["finding 1", "finding 2", "..."],\n'
                                '  "specialty": "medical specialty needed (e.g. cardiologist, endocrinologist)"\n'
                                "}\n"
                                "severity HIGH means the patient urgently needs a doctor. "
                                "Be accurate and compassionate."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": state["image_b64"]},
                        },
                    ],
                }
            ],
            temperature=0.3,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
        )

        raw = response.choices[0].message.content or "{}"
        data = _extract_json(raw)

        return {
            "condition": data.get("condition", "Unknown"),
            "severity": data.get("severity", "LOW").upper(),
            "summary": data.get("summary", ""),
            "key_findings": data.get("key_findings", []),
            "specialty": data.get("specialty", "general physician"),
            "error": None,
        }
    except Exception as e:
        logger.error(f"analyze_report_node error: {e}")
        return {"error": str(e), "severity": "LOW"}


# ─── Node 2: Generate diet plan ───────────────────────────────────────────────

def generate_diet_plan_node(state: HealthState) -> dict:
    """Generate personalised diet plan cards based on the condition."""
    prompt = (
        f"The patient has been diagnosed with: {state.get('condition', 'a health issue')}.\n"
        f"Summary: {state.get('summary', '')}\n\n"
        "Generate a personalised 5-item diet plan. Respond ONLY with a JSON array:\n"
        "[\n"
        "  {\n"
        '    "meal": "Meal name",\n'
        '    "description": "Why this helps",\n'
        '    "timing": "Morning|Afternoon|Evening|Night",\n'
        '    "icon": "emoji",\n'
        '    "macros": {"protein": "Xg", "carbs": "Xg", "fat": "Xg", "calories": "X kcal"}\n'
        "  }\n"
        "]"
    )
    try:
        raw = _chat([{"role": "user", "content": prompt}])
        plan = _extract_json(raw)
        return {"diet_plan": plan}
    except Exception as e:
        logger.error(f"generate_diet_plan_node error: {e}")
        return {"diet_plan": []}


# ─── Node 3: Generate exercise plan ──────────────────────────────────────────

def generate_exercise_plan_node(state: HealthState) -> dict:
    """Generate personalised exercise cards (gentle, suitable for the condition)."""
    prompt = (
        f"The patient has: {state.get('condition', 'a health issue')}. "
        f"Severity: {state.get('severity', 'LOW')}.\n\n"
        "Generate 5 safe, personalised exercise recommendations. "
        "Respond ONLY with a JSON array:\n"
        "[\n"
        "  {\n"
        '    "name": "Exercise name",\n'
        '    "description": "How to do it",\n'
        '    "duration": "e.g. 10 minutes",\n'
        '    "reps": "e.g. 3 sets x 10 reps (or null if time-based)",\n'
        '    "difficulty": "Easy|Moderate|Hard",\n'
        '    "icon": "emoji",\n'
        '    "benefit": "Why this helps the condition"\n'
        "  }\n"
        "]"
    )
    try:
        raw = _chat([{"role": "user", "content": prompt}])
        plan = _extract_json(raw)
        return {"exercise_plan": plan}
    except Exception as e:
        logger.error(f"generate_exercise_plan_node error: {e}")
        return {"exercise_plan": []}


# ─── Node 4: Generate home remedies ──────────────────────────────────────────

def generate_home_remedies_node(state: HealthState) -> dict:
    """Generate home remedy cards for the condition."""
    prompt = (
        f"The patient has: {state.get('condition', 'a health issue')}.\n\n"
        "Suggest 4 evidence-based home remedies. "
        "Respond ONLY with a JSON array:\n"
        "[\n"
        "  {\n"
        '    "remedy": "Remedy name",\n'
        '    "icon": "emoji",\n'
        '    "ingredients": ["ingredient 1", "ingredient 2"],\n'
        '    "instructions": ["Step 1", "Step 2"],\n'
        '    "frequency": "How often to do it",\n'
        '    "benefit": "Why it helps"\n'
        "  }\n"
        "]"
    )
    try:
        raw = _chat([{"role": "user", "content": prompt}])
        remedies = _extract_json(raw)
        return {"home_remedies": remedies}
    except Exception as e:
        logger.error(f"generate_home_remedies_node error: {e}")
        return {"home_remedies": []}


# ─── Node 5: Check severity & decide routing ─────────────────────────────────

def check_severity_node(state: HealthState) -> dict:
    """Pass-through node — routing decision is handled by the conditional edge."""
    return {}


# ─── Node 6: Find nearby doctors ─────────────────────────────────────────────

def find_doctors_node(state: HealthState) -> dict:
    """Search for nearby doctors using DuckDuckGo based on specialty + location."""
    specialty = state.get("specialty", "general physician")
    location = state.get("location") or {}
    city = location.get("city", "")

    doctors = search_doctors(specialty=specialty, city=city)
    return {"nearby_doctors": doctors}
