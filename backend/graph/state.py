from typing import TypedDict, Optional, List
from langchain_core.messages import BaseMessage


class RAGState(TypedDict):
    """Shared state that flows through the RAG LangGraph pipeline."""
    session_id: str
    question: str
    
    # RAG context
    global_profile: Optional[str]
    retrieved_context: Optional[str]
    
    # Chat history
    messages: List[BaseMessage]
    
    # Error passthrough
    error: Optional[str]
