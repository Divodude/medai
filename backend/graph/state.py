from typing import TypedDict, Optional, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class RAGState(TypedDict):
    """Shared state that flows through the RAG LangGraph pipeline."""
    session_id: str
    question: str
    
    # RAG context
    global_profile: Optional[str]
    retrieved_context: Optional[str]
    
    # Chat history (with reducer so ToolNode and agent append messages rather than overwriting)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Error passthrough
    error: Optional[str]
