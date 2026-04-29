from langchain.messages import HumanMessage, AIMessage
import os
from langgraph.graph import StateGraph
from .prompt import CODING_SANDBOX_AGENT_PROMPT
from ....PlotGraph.Graph.tools import CodeInterpreterTool


def data_analysis_agent(
    sandbox_graph: StateGraph, paths: [str], prompt: str
) -> AIMessage:
    python_env = CodeInterpreterTool(mount_paths=paths)

    mount_infromation = "\nMounted data paths:\n"
    for path in paths:
        mount_infromation += f"- /home/user/mounted/{os.path.basename(path)}\n"
    mount_infromation += "\nUser input:\n"

    messages = [
        HumanMessage(
            content=CODING_SANDBOX_AGENT_PROMPT.format_map(
                {"query": prompt, "mounted_data": mount_infromation}
            )
        ),
    ]

    final_state = sandbox_graph.invoke(
        {"messages": messages}, config={"configurable": {"python_env": python_env}}
    )
    final_state_message = final_state["messages"][-1]

    python_env.sandbox.kill()

    return final_state_message
