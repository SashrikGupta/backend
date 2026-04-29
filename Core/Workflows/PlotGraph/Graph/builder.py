from langgraph.graph import START, END, StateGraph
from .nodes import prompt_node, code_node, analysis_node
from .states import PlotAgent_InputState, PlotAgent_OutputState
from langchain.chat_models import BaseChatModel


def get_plotting_agent(
    prompt_llm: BaseChatModel, image_llm: BaseChatModel, sandbox_graph: StateGraph
) -> StateGraph:
    """Build and compile the auto-tagging LangGraph pipeline.

    Args:
        prompt_llm : standard langchain llm
        image_llm : langchain_llm with image and structure output capabilities
        sandbox_graph : sandbox graph

    Returns:
        A compiled `StateGraph` instance representing the plot workflow.
    """

    plot_graph_builder = StateGraph(
        PlotAgent_InputState, output_schema=PlotAgent_OutputState
    )
    plot_graph_builder.add_node("prompt_node", prompt_node(prompt_llm))
    plot_graph_builder.add_node("code_node", code_node(sandbox_graph))
    plot_graph_builder.add_node("analysis_node", analysis_node(image_llm))
    plot_graph_builder.add_edge(START, "prompt_node")
    plot_graph_builder.add_edge("prompt_node", "code_node")
    plot_graph_builder.add_edge("code_node", "analysis_node")
    plot_graph_builder.add_edge("analysis_node", END)

    plot_graph = plot_graph_builder.compile()

    return plot_graph
