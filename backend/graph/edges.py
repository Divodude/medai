from backend.graph.state import HealthState


def should_search_doctors(state: HealthState) -> str:
    """
    Conditional edge: after check_severity_node.
    Routes to find_doctors_node only if severity is MEDIUM or HIGH.
    Otherwise ends the graph.
    """
    severity = (state.get("severity") or "LOW").upper()
    if severity in ("MEDIUM", "HIGH"):
        return "find_doctors"
    return "__end__"
