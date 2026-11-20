from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.change_correlator import change_correlator
from src.agents.error_parser import error_parser
from src.agents.history_retriever import history_retriever
from src.agents.hypothesis_agent import hypothesis_agent
from src.agents.report_writer import report_writer


class IncidentState(TypedDict, total=False):
    raw_input: str
    sanitized_input: str
    parsed_error: dict[str, Any]
    retrieved_incidents: list[dict[str, Any]]
    recent_commits: list[dict[str, Any]]
    hypotheses: list[dict[str, Any]]
    report_markdown: str
    warnings: list[str]
    session_id: str
    repo_url: str | None


def build_retrieval_pipeline():
    graph = StateGraph(IncidentState)
    graph.add_node("error_parser", error_parser)
    graph.add_node("history_retriever", history_retriever)
    graph.add_node("change_correlator", change_correlator)
    graph.add_edge(START, "error_parser")
    graph.add_edge("error_parser", "history_retriever")
    graph.add_edge("history_retriever", "change_correlator")
    graph.add_edge("change_correlator", END)
    return graph.compile()


def build_pipeline():
    graph = StateGraph(IncidentState)
    graph.add_node("error_parser", error_parser)
    graph.add_node("history_retriever", history_retriever)
    graph.add_node("change_correlator", change_correlator)
    graph.add_node("hypothesis_agent", hypothesis_agent)
    graph.add_node("report_writer", report_writer)
    graph.add_edge(START, "error_parser")
    graph.add_edge("error_parser", "history_retriever")
    graph.add_edge("history_retriever", "change_correlator")
    graph.add_edge("change_correlator", "hypothesis_agent")
    graph.add_edge("hypothesis_agent", "report_writer")
    graph.add_edge("report_writer", END)
    return graph.compile()
