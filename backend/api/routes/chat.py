"""
POST /chat — Follow-up questions with full patient context and doctor search tools.
Uses ChatGroq with tool-calling to fetch real-time data when asked.
"""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session as DBSession

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.db.database import get_db
from backend.db import crud
from backend.tools.doctor_search import search_doctors as ddg_search_doctors

router = APIRouter()

# ─── Tool ─────────────────────────────────────────────────────────────────

@tool
def search_nearby_doctors(specialty: str, location: str):
    """
    Search for doctors or clinics of a specific specialty in a given city or location.
    ALWAYS call this tool when the user asks for doctors, clinics, physicians, or specialists.
    Do NOT answer from memory — only use results returned by this tool.
    """
    return ddg_search_doctors(specialty, location)


TOOLS = [search_nearby_doctors]

# ─── Models ───────────────────────────────────────────────────────────────

class AnalysisContextPayload(BaseModel):
    condition: Optional[str] = None
    severity: Optional[str] = None
    summary: Optional[str] = None
    key_findings: Optional[List[str]] = None
    specialty: Optional[str] = None
    location: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    analysis_context: Optional[AnalysisContextPayload] = None


# ─── System Prompt ────────────────────────────────────────────────────────

SYSTEM_TEMPLATE = """\
You are a concise AI health assistant. Help patients interpret medical reports \
and provide practical health advice.

═══ CRITICAL: DOCTOR SEARCH RULES ═══
• If the user asks for doctors, clinics, physicians, or specialists — \
ALWAYS call the `search_nearby_doctors` tool. No exceptions.
• NEVER invent, guess, or fabricate doctors, phone numbers, addresses, or URLs.
• If the tool returns no results, say clearly: "I couldn't find specific doctors \
in [city]. Try Google Maps or Practo.com for local listings."

═══ RESPONSE STYLE ═══
• Be SHORT. 2-4 sentences for normal answers.
• Use **bold** for key terms. Use bullet lists ONLY for doctor results.
• Format found doctors as: **Name** — [specialty] — [Google Maps link]
• End with: *I'm an AI, not a doctor. Please verify with a medical professional.*

═══ PATIENT CONTEXT ═══
{context_block}

USER LOCATION: {location}
"""


def _build_system_prompt(req: ChatRequest, db_analyses) -> str:
    ctx = req.analysis_context

    context_str = "No report uploaded."
    location = "Unknown — the user may provide it in the message."

    if ctx and ctx.condition:
        context_str = (
            f"Condition: **{ctx.condition}** (Severity: {ctx.severity})\n"
            f"Summary: {ctx.summary}\n"
            f"Key Findings: {', '.join(ctx.key_findings or [])}\n"
            f"Recommended Specialist: {ctx.specialty}"
        )
        if ctx.location:
            location = ctx.location
    elif analyses:
        latest = db_analyses[0]
        context_str = (
            f"Condition: **{latest.condition}** (Severity: {latest.severity})\n"
            f"Summary: {latest.summary}\n"
            f"Recommended Specialist: {latest.specialty}"
        )

    # Also extract location from message if user stated it inline
    return SYSTEM_TEMPLATE.format(context_block=context_str, location=location)


# ─── Route ────────────────────────────────────────────────────────────────

@router.post("/chat")
async def chat(req: ChatRequest, db: DBSession = Depends(get_db)):
    analyses = crud.get_analyses_for_session(db, req.session_id)
    system_prompt = _build_system_prompt(req, analyses)

    llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0.3)
    llm_with_tools = llm.bind_tools(TOOLS)

    async def generate():
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=req.message),
        ]

        # Step 1: Let model decide whether to call a tool
        ai_msg = llm_with_tools.invoke(messages)

        if ai_msg.tool_calls:
            messages.append(ai_msg)
            # Execute each tool call
            for tc in ai_msg.tool_calls:
                result = search_nearby_doctors.invoke(tc["args"])
                messages.append(ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    tool_call_id=tc["id"]
                ))
            # Step 2: Stream final answer with tool results
            for chunk in llm.stream(messages):
                if chunk.content:
                    yield chunk.content
        else:
            # Stream direct answer
            for chunk in llm.stream(messages):
                if chunk.content:
                    yield chunk.content

    return StreamingResponse(generate(), media_type="text/plain")
