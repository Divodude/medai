import os
from langchain_core.messages import SystemMessage, ToolMessage

from graph.state import RAGState
from tools.doctor_search import search_doctors as ddg_search_doctors
from llm_provider import get_llm, get_embeddings
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma

# --- Tools ---
@tool
def search_nearby_doctors(specialty: str, location: str):
    """
    Search for doctors or clinics of a specific specialty in a given city or location.
    ALWAYS call this tool when the user asks for doctors, clinics, physicians, or specialists.
    """
    return ddg_search_doctors(specialty, location)

TOOLS = [search_nearby_doctors]

# --- Nodes ---
def retrieve_node(state: RAGState) -> dict:
    """Retrieve relevant context from ChromaDB based on the question."""
    session_id = state.get("session_id")
    question = state.get("question", "")
    
    persist_directory = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
    if not os.path.exists(persist_directory):
        return {"retrieved_context": "No documents uploaded yet."}
        
    try:
        embeddings = get_embeddings()
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        
        # Filter by session_id
        retriever = vectorstore.as_retriever(
            search_kwargs={"filter": {"session_id": session_id}, "k": 5}
        )
        
        docs = retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        return {"retrieved_context": context if context else "No specific info found in report."}
    except Exception as e:
        return {"retrieved_context": f"Error retrieving context: {str(e)}"}


def agent_node(state: RAGState) -> dict:
    """Generate answer using LLM, context, and chat history."""
    llm = get_llm(temperature=0.3)
    llm_with_tools = llm.bind_tools(TOOLS)
    
    context = state.get("retrieved_context", "None")
    global_profile = state.get("global_profile", "None")
    
    system_prompt = (
        "You are an AI health assistant answering patient questions based on their uploaded medical report. "
        "Use the retrieved context from their report to answer the question. "
        "If they ask for doctors, always call the search_nearby_doctors tool.\n\n"
        f"--- GLOBAL PATIENT PROFILE ---\n{global_profile}\n------------------------------\n\n"
        f"--- PATIENT REPORT CONTEXT ---\n{context}\n------------------------------\n"
    )
    
    # Prepend system message to history and add current question
    messages = [SystemMessage(content=system_prompt)] + state.get("messages", [])
    
    # We don't append question as a new message if it's already the last human message in state.messages
    # Typically, the router (chat.py) will append the question to state["messages"].
    
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}
