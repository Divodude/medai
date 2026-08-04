"""
POST /chat — Follow-up questions with full patient context and doctor search tools.
Uses LangGraph RAG pipeline to retrieve context and answer questions.
"""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from langchain_core.messages import HumanMessage, AIMessage

from db.database import get_db
from db import crud
from graph.builder import rag_graph

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def chat(req: ChatRequest, db: DBSession = Depends(get_db)):
   
    analyses = crud.get_analyses_for_session(db, req.session_id)
    analysis = analyses[0] if analyses else None
    global_profile = analysis.structured_summary if analysis else None

    initial_state = {
        "session_id": req.session_id,
        "question": req.message,
        "global_profile": global_profile,
        "messages": [HumanMessage(content=req.message)]
    }

   
    
    async def generate():
       
        result = await rag_graph.ainvoke(initial_state)
        
       
        messages = result.get("messages", [])
        if not messages:
            yield "Sorry, I couldn't process your request."
            return
            
        final_message = messages[-1]
        
   
        if hasattr(final_message, "content"):
            content = final_message.content
          
            chunk_size = 20
            for i in range(0, len(content), chunk_size):
                yield content[i:i+chunk_size]
        else:
            yield str(final_message)

    return StreamingResponse(generate(), media_type="text/plain")
