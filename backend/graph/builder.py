from langgraph.graph import StateGraph, END
from backend.graph.state import HealthState
from backend.graph.nodes import (
    analyze_report_node,
    generate_diet_plan_node,
    generate_exercise_plan_node,
    generate_home_remedies_node,
    check_severity_node,
    find_doctors_node,
)
from backend.graph.edges import should_search_doctors


def build_graph():
    """Compile and return the LangGraph health assistant pipeline."""
    workflow = StateGraph(HealthState)

    # Register nodes
    workflow.add_node("analyze_report", analyze_report_node)
    workflow.add_node("generate_diet", generate_diet_plan_node)
    workflow.add_node("generate_exercise", generate_exercise_plan_node)
    workflow.add_node("generate_remedies", generate_home_remedies_node)
    workflow.add_node("check_severity", check_severity_node)
    workflow.add_node("find_doctors", find_doctors_node)

    # Entry point
    workflow.set_entry_point("analyze_report")

    # Linear pipeline: analyze → parallel-ish generation → severity check
    workflow.add_edge("analyze_report", "generate_diet")
    workflow.add_edge("generate_diet", "generate_exercise")
    workflow.add_edge("generate_exercise", "generate_remedies")
    workflow.add_edge("generate_remedies", "check_severity")

    # Conditional: search doctors only if severity is MEDIUM or HIGH
    workflow.add_conditional_edges(
        "check_severity",
        should_search_doctors,
        {
            "find_doctors": "find_doctors",
            "__end__": END,
        },
    )
    workflow.add_edge("find_doctors", END)

    return workflow.compile()


# Singleton graph instance
health_graph = build_graph()
