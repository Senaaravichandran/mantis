"""LangGraph StateGraph supervisor — orchestrates the 6 MANTIS agents."""

from langgraph.graph import StateGraph, END

from .state import MANTISState
from .router import (
    route_after_sentinel,
    route_after_analyst,
    route_after_planner,
    route_after_reporter,
    route_after_contractor,
    route_after_regulator,
)
from ..agents.sentinel_agent import SentinelAgent
from ..agents.analyst_agent import AnalystAgent
from ..agents.planner_agent import PlannerAgent
from ..agents.reporter_agent import ReporterAgent
from ..agents.contractor_agent import ContractorAgent
from ..agents.regulator_agent import RegulatorAgent


def build_mantis_graph(llm=None, db_session=None) -> StateGraph:
    """Build the MANTIS multi-agent LangGraph.

    The graph routes between agents based on the state:
    Sentinel -> (if anomaly) Analyst -> (if high risk) Planner -> Reporter
                                                                    |
                                                        Contractor -> Regulator
    """
    # Initialize agents
    sentinel = SentinelAgent(llm=llm, db_session=db_session)
    analyst = AnalystAgent(llm=llm, db_session=db_session)
    planner = PlannerAgent(llm=llm, db_session=db_session)
    reporter = ReporterAgent(llm=llm, db_session=db_session)
    contractor = ContractorAgent(llm=llm, db_session=db_session)
    regulator = RegulatorAgent(llm=llm, db_session=db_session)

    # Build graph
    graph = StateGraph(MANTISState)

    # Add agent nodes
    graph.add_node("sentinel", sentinel.run)
    graph.add_node("analyst", analyst.run)
    graph.add_node("planner", planner.run)
    graph.add_node("reporter", reporter.run)
    graph.add_node("contractor", contractor.run)
    graph.add_node("regulator", regulator.run)

    # Set entry point
    graph.set_entry_point("sentinel")

    # Add conditional edges
    graph.add_conditional_edges("sentinel", route_after_sentinel, {
        "analyst": "analyst",
        "__end__": END,
    })
    graph.add_conditional_edges("analyst", route_after_analyst, {
        "planner": "planner",
        "reporter": "reporter",
        "__end__": END,
    })
    graph.add_conditional_edges("planner", route_after_planner, {
        "reporter": "reporter",
        "__end__": END,
    })
    graph.add_conditional_edges("reporter", route_after_reporter, {
        "contractor": "contractor",
        "regulator": "regulator",
        "__end__": END,
    })
    graph.add_conditional_edges("contractor", route_after_contractor, {
        "regulator": "regulator",
    })
    graph.add_conditional_edges("regulator", route_after_regulator, {
        "__end__": END,
    })

    return graph.compile()
