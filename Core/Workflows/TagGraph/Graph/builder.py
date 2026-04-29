from functools import partial

from langgraph.graph import START, END, StateGraph

from .routers import spawn_batches
from .nodes import (
    data_ingestion_node,
    batch_node,
    batch_post_process_node,
    cluster_node,
)
from .states import GeneralState
from langchain.chat_models import BaseChatModel
from typing import List


def get_auto_tagging_graph(
    batch_llm: List[BaseChatModel], cluster_llm: BaseChatModel
) -> StateGraph:
    """Build and compile the auto-tagging LangGraph pipeline.

    Args:
        config: Configuration dictionary for graph construction.
            Expected keys:
                - "model_name": Name of the LLM model to use for batch and
                  clustering agents.

    Returns:
        A compiled `StateGraph` instance representing the auto-tagging workflow.
    """

    graph_builder = StateGraph(GeneralState)
    # Nodes
    graph_builder.add_node("data_ingestion", data_ingestion_node)
    graph_builder.add_node("batch_agent", batch_node(batch_llm))
    graph_builder.add_node("postprocess", batch_post_process_node)
    graph_builder.add_node("cluster_agent", cluster_node(cluster_llm))

    # Edges
    graph_builder.add_edge(START, "data_ingestion")

    graph_builder.add_conditional_edges(
        "data_ingestion",
        partial(
            spawn_batches,
            target_node="batch_agent",
        ),
        ["batch_agent"],
    )

    graph_builder.add_edge("batch_agent", "postprocess")
    graph_builder.add_edge("postprocess", "cluster_agent")
    graph_builder.add_edge("cluster_agent", END)

    # Compile
    auto_tag_graph = graph_builder.compile()

    return auto_tag_graph
