from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

from graph.state import RAGState
from graph.nodes import retrieve_node, agent_node, TOOLS


def build_graph():
    """Compile and return the RAG LangGraph health assistant pipeline."""
    workflow = StateGraph(RAGState)

    # Register nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(TOOLS))

    # Flow
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "agent")
    
    # Conditional logic: if agent returns tool calls -> tools, else -> END
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            "__end__": END,
        }
    )
    
    # After tools run, go back to agent to synthesize answer
    workflow.add_edge("tools", "agent")

    return workflow.compile()

# Singleton graph instance
rag_graph = build_graph()
