from langchain.messages import HumanMessage, SystemMessage, AIMessage
from .prompt import CODER_INSTRUCTION_PROMPT, CODER_SYSTEM_PROMPT
import os
import shutil
from langgraph.graph import StateGraph
from ...Graph.tools import CodeInterpreterTool


def code_agent(
    sandbox_graph: StateGraph,
    path: str,
    graph_prompt: str,
    output_dir_name: str,
    dataset_info: str,
    dataset_eg: str,
    product_id: int,
) -> AIMessage:
    python_env = CodeInterpreterTool(mount_paths=[path])
    instruction_prompt = ""
    instruction_prompt += CODER_INSTRUCTION_PROMPT
    instruction_prompt += "\nMounted data paths:\n"
    instruction_prompt += f"- /home/user/mounted/{os.path.basename(path)}\n"
    instruction_prompt += "\nUser input:\n"
    instruction_prompt += "\nDataset info:\n"
    instruction_prompt += str(dataset_info)
    instruction_prompt += "\nsome examples from Dataset:\n"
    instruction_prompt += str(dataset_eg)

    instruction_prompt += graph_prompt
    messages = [
        SystemMessage(content=CODER_SYSTEM_PROMPT),
        HumanMessage(content=instruction_prompt),
    ]

    final_state = sandbox_graph.invoke(
        {"messages": messages}, config={"configurable": {"python_env": python_env}}
    )

    if os.path.exists(output_dir_name):
        shutil.rmtree(output_dir_name)
    os.makedirs(output_dir_name)
    python_env.zip_and_close(output_dir=output_dir_name)

    return final_state["messages"][-1]
