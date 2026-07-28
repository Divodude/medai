"""
POST /chat — Follow-up questions with full patient context and doctor search tools.
Uses LangGraph RAG pipeline to retrieve context and answer questions.
"""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session as DBSession

from langchain_core.messages import HumanMessage, AIMessage

from db.database import get_db
from db import crud
from graph.builder import rag_graph

router = APIRouter()

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


@router.post("/chat")
async def chat(req: ChatRequest, db: DBSession = Depends(get_db)):
    # We will build a basic chat history. In a full production app, 
    # we would persist this history to the database per session_id.
    
    analyses = crud.get_analyses_for_session(db, req.session_id)
    analysis = analyses[0] if analyses else None
    global_profile = analysis.structured_summary if analysis else None

    # Initialize state
    initial_state = {
        "session_id": req.session_id,
        "question": req.message,
        "global_profile": global_profile,
        "messages": [HumanMessage(content=req.message)]
    }

   
    
    async def generate():
        # Invoke the LangGraph pipeline
        result = await rag_graph.ainvoke(initial_state)
        
        # The final message is the last AIMessage in the state
        messages = result.get("messages", [])
        if not messages:
            yield "Sorry, I couldn't process your request."
            return
            
        final_message = messages[-1]
        
        # Stream the content back
        if hasattr(final_message, "content"):
            content = final_message.content
            # Simulate streaming by yielding chunks
            chunk_size = 20
            for i in range(0, len(content), chunk_size):
                yield content[i:i+chunk_size]
        else:
            yield str(final_message)

    return StreamingResponse(generate(), media_type="text/plain")
