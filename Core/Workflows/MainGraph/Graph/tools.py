from pathlib import Path
import os
import json
from pathlib import Path

import pandas as pd

from pydantic import BaseModel, Field

from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolRuntime

from ..Agent import data_analysis_agent
import json


def check_product(product_id: int) -> bool:
    """
    checks if analysis of a perticular product has been done or not
    """
    core_path = Path(__file__).resolve().parents[3]
    config_path = core_path / "Results" / f"pr_id_{product_id}.json"

    return config_path.exists()


def save_product_data(product_id: int, data: dict) -> None:
    """
    saves the analysis of a perticular product
    """
    core_path = Path(__file__).resolve().parents[3]
    config_path = core_path / "Results" / f"pr_id_{product_id}.json"

    with open(config_path, "w") as f:
        json.dump(data, f)


def load_product(product_id: int) -> dict:
    """
    loads the analysis of a perticular product
    """
    core_path = Path(__file__).resolve().parents[3]
    config_path = core_path / "Results" / f"pr_id_{product_id}.json"

    with open(config_path, "r") as f:
        return json.load(f)


class ToolArgs(BaseModel) : 
    prompt : str = Field(description="prompt that would be given to the Agent")


@tool(args_schema=ToolArgs)
def data_analysis_tool(prompt : str , runtime : ToolRuntime , config: RunnableConfig) -> str : 
    """
    Performs analytical reasoning on preprocessed product review data.
    Args:
        prompt (str):
            Natural language prompt describing the type of analysis or insights
            that should be extracted from the review data. The prompt should focus
            on analytical goals
    Returns:
        str:
            A textual analytical summary containing insights derived from the
            review dataset based on the provided prompt.
    """
    sandbox_graph = config["configurable"]["sandbox_graph"]
    backend_root = Path(__file__).resolve().parents[4]
    temp_dir = backend_root / f"temp_{runtime.state['run_id']}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    review_list_path = str(temp_dir / "reviews_list.csv")
    review_analysis_path = str(temp_dir / "reviews_analysis.csv")
    review_data = runtime.state["review_analysis"]

    review_analysis_df = pd.DataFrame(review_data["result"])
    review_list = review_data["review_list"]
    review_list_df = []
    for id, review in enumerate(review_list):
        review_list_df.append({"review_id": id, "review": review})
    review_list_df = pd.DataFrame(review_list_df)
    review_list_df.rename(columns={"rid": "review_id"}, inplace=True)
    review_list_df.to_csv(review_list_path)
    review_analysis_df.to_csv(review_analysis_path)
    paths = [review_list_path, review_analysis_path]

    analysis = data_analysis_agent(sandbox_graph, paths, prompt)

    return analysis


@tool(args_schema=ToolArgs)
def plot_generation_tool(prompt : str , runtime : ToolRuntime , config: RunnableConfig) -> str:
    """
    Generates visualizations from processed product review data.
    Args:
        prompt (str):
            Natural language prompt describing the visualization that should be
            generated from the review data. 
    Returns:
        str:
            A textual response describing the generated plots along with any
            artifact references (such as file paths and plot metadata)
    """
    plot_agent = config["configurable"]["plot_agent"]
    plot_result = plot_agent.invoke(
        {
            "run_id": runtime.state["run_id"],
            "product_id": runtime.state["product_id"],
            "query": prompt,
            "analysis_result": runtime.state["review_analysis"]["result"],
        }
    )
    return f" \n here are the results for plot generation \n {str(plot_result)} "
