from .nodes import (
    result_loader_node,
    supervisor_node,
    review_preprocess_node,
    reporter_node,
)
from .routers import base_router
from .states import MainState
from ...TagGraph import get_auto_tagging_graph
from ...SandBoxGraph import get_sandbox_graph
from ...PlotGraph import get_plotting_agent
from ....LLMS import build_llm_factory

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from .tools import data_analysis_tool, plot_generation_tool

PREPROCESS = "preprocess_node"
LOADER = "loader_node"
SUPERVISOR = "supervisor_node"
TOOL_NODE = "tool_node"
REPORTER = "reporter_node"

def build_main_graph():
    llm_factory = build_llm_factory()
    sandbox_graph_data = get_sandbox_graph(llm_factory["coder_llm_data_analysis"][0])
    sandbox_graph_plot = get_sandbox_graph(llm_factory["coder_llm_plotting"][0])
    plot_agent = get_plotting_agent(
        sandbox_graph=sandbox_graph_plot,
        prompt_llm=llm_factory["planner_llm"][0],
        image_llm=llm_factory["image_llm"][0],
    )
    tag_agent = get_auto_tagging_graph(
        batch_llm=llm_factory["batch_llms"], cluster_llm=llm_factory["planner_llm"][0]
    )

    tools = [data_analysis_tool, plot_generation_tool]

    main_graph_builder = StateGraph(MainState)

    main_graph_builder.add_node(PREPROCESS, review_preprocess_node(tag_agent))
    main_graph_builder.add_node(LOADER, result_loader_node)
    main_graph_builder.add_node(SUPERVISOR, supervisor_node(llm_factory["planner_llm"][0], tools))
    main_graph_builder.add_node(TOOL_NODE, ToolNode(tools))
    main_graph_builder.add_node(REPORTER, reporter_node(llm_factory["report_llm"][0]))

    main_graph_builder.add_conditional_edges(
        START,
        base_router([LOADER, PREPROCESS]),
        [LOADER, PREPROCESS],
    )

    main_graph_builder.add_edge(PREPROCESS, LOADER)
    main_graph_builder.add_edge(LOADER, SUPERVISOR)

    main_graph_builder.add_conditional_edges(
        SUPERVISOR,
        tools_condition,
        {
            "tools": TOOL_NODE,
            "__end__": REPORTER,
        },
    )

    main_graph_builder.add_edge(TOOL_NODE, SUPERVISOR)
    main_graph_builder.add_edge(REPORTER, END)

    main_graph = main_graph_builder.compile()

    return main_graph


main_graph_object = build_main_graph()
