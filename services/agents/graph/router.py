"""Conditional edge routing logic for the MANTIS agent graph."""

from .state import MANTISState


def route_after_sentinel(state: MANTISState) -> str:
    """Route after Sentinel agent completes."""
    if state.anomaly_detected:
        return "analyst"
    return "__end__"


def route_after_analyst(state: MANTISState) -> str:
    """Route after Analyst agent completes."""
    if state.risk_score is not None and state.risk_score >= 60:
        return "planner"
    elif state.risk_score is not None and state.risk_score >= 30:
        return "reporter"
    return "__end__"


def route_after_planner(state: MANTISState) -> str:
    """Route after Planner agent completes."""
    if state.work_order_draft:
        return "reporter"
    return "__end__"


def route_after_reporter(state: MANTISState) -> str:
    """Route after Reporter agent completes."""
    if state.work_order_approved:
        return "contractor"
    # Check if compliance review needed
    if state.risk_score and state.risk_score >= 70:
        return "regulator"
    return "__end__"


def route_after_contractor(state: MANTISState) -> str:
    """Route after Contractor agent completes."""
    return "regulator"


def route_after_regulator(state: MANTISState) -> str:
    """Route after Regulator agent completes."""
    return "__end__"


def should_continue(state: MANTISState) -> str:
    """General routing: check next_agent field."""
    if state.next_agent:
        return state.next_agent
    return "__end__"
