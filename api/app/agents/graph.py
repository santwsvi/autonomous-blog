"""LangGraph StateGraph — orchestrates the content generation pipeline.

Flow: Researcher → Writer → Editor → (loop if score < 0.85) → SEO → Publisher
"""

import structlog
from langgraph.graph import END, StateGraph

from app.agents.nodes.editor import editor
from app.agents.nodes.publisher import publisher
from app.agents.nodes.researcher import researcher
from app.agents.nodes.seo_optimizer import seo_optimizer
from app.agents.nodes.writer import writer
from app.agents.state import AgentState

logger = structlog.get_logger()


def should_revise(state: AgentState) -> str:
    """Conditional edge: route back to writer or forward to SEO."""
    if state.approved:
        logger.info("editor_approved", score=state.quality_scores.overall, iteration=state.iteration)
        return "seo_optimizer"

    if state.iteration >= state.max_iterations:
        logger.warning(
            "max_iterations_reached",
            score=state.quality_scores.overall,
            iteration=state.iteration,
        )
        # Publish anyway with whatever we have
        return "seo_optimizer"

    logger.info(
        "editor_revision_requested",
        score=state.quality_scores.overall,
        iteration=state.iteration,
    )
    return "writer"


def build_graph() -> StateGraph:
    """Build and compile the content generation graph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_node("editor", editor)
    graph.add_node("seo_optimizer", seo_optimizer)
    graph.add_node("publisher", publisher)

    # Define edges
    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "editor")
    graph.add_conditional_edges("editor", should_revise, {"writer": "writer", "seo_optimizer": "seo_optimizer"})
    graph.add_edge("seo_optimizer", "publisher")
    graph.add_edge("publisher", END)

    return graph.compile()


# Singleton compiled graph
generation_graph = build_graph()
