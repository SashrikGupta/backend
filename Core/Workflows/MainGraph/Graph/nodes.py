from typing import List ,  Callable
from langgraph.graph import StateGraph
from langchain.chat_models import BaseChatModel
from Core.Workflows.MainGraph.Graph.tools import save_product_data, load_product
from langchain.messages import AIMessage
from .states import MainState
from ..Agent import supervisor_agent ,  reporter_agent
import os
import pandas as pd
from langchain.tools import BaseTool
import re
import base64
import mimetypes
from pathlib import Path


def embed_local_images_as_base64(markdown: str, base_path: str | None = None) -> str:
    base_path = Path(base_path)
    pattern = re.compile(r"!\[(.*?)\]\(@@add_image_(.*?)@@\)")  # remove optional \s*
    supported_extensions = [".png", ".jpg", ".jpeg", ".webp", ".gif"]

    def replace_match(match):
        alt_text = match.group(1)
        base_filename = match.group(2).strip()  # strip spaces
        image_file = None
        for ext in supported_extensions:
            candidate = base_path / f"{base_filename}{ext}"
            print("Checking:", candidate, candidate.exists())
            if candidate.exists():
                image_file = candidate
                break
        if image_file is None:
            print(f"No file found for {base_filename}")
            return match.group(0)
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"![{alt_text}](data:image/png;base64,{encoded})"

    return pattern.sub(replace_match, markdown)


def result_loader_node(state: MainState) -> MainState:
    return {"review_analysis": load_product(state["product_id"])}


def review_preprocess_node(tag_agent: StateGraph):
    def tag_review_preprocess_node(state: MainState) -> MainState:
        sub_graphs_output = tag_agent.invoke({"product_id": state["product_id"]})
        save_product_data(state["product_id"], sub_graphs_output)
        return {}
    return tag_review_preprocess_node


def supervisor_node(llm:BaseChatModel , tools : List[BaseTool]) -> Callable[[MainState] , MainState] : 
    def llm_supervisor_node(state:MainState)->MainState : 
        user_prompt = state["messages"][-1].content
        current_idx = len(state["messages"])
        llm_with_tools = llm.bind_tools(tools)
        insight = supervisor_agent(llm_with_tools , user_prompt)
        return {
            "messages" : [insight] , 
            "user_query": user_prompt,
            "chain_start": current_idx,
        }
    return llm_supervisor_node

def reporter_node(llm: BaseChatModel) -> Callable[[MainState], MainState]:
    def llm_reporter_node(state: MainState) -> MainState:
        message_chain = state["messages"][state["chain_start"] - 1 :]
        result = reporter_agent(llm, message_chain, state["user_query"])
        backend_root = Path(__file__).resolve().parents[4]
        base_path = str(backend_root / f"sandbox_output_{state['run_id']}")
        result = embed_local_images_as_base64(result.content, base_path)
        return {"messages": [AIMessage(content=result)]}

    return llm_reporter_node
