from collections import defaultdict
from .states import GeneralState, BatchInputState
from typing import List
from .datasets import review_dataset
from ..Agent.BatchAgent.prompt import SYSTEM_PROMPT
from typing import Callable
from langchain.chat_models import BaseChatModel
from ..Agent import batch_agent, cluster_agent
import tiktoken

MAX_TOK = 3000


def batch_post_process_node(state: GeneralState) -> GeneralState:
    """Post-process batch results and prepare clustering inputs.

    Args:
        state: Graph state containing combined batch review data.

    Returns:
        Updated state with clustered title groups, key-to-review mapping,
        and original results.
    """
    grouped_data = defaultdict(list)
    current_id = 0
    res = state["combined_data"]
    for data in res:
        for review in data["review_data"]:
            clean_title = review["title"].lower()
            review["key_id"] = current_id
            grouped_data[clean_title].append(current_id)
            current_id += 1
    final_output = [{"title": title, "ids": ids} for title, ids in grouped_data.items()]
    key_id_to_data_mapping = {}
    for data in res:
        for review in data["review_data"]:
            key_id = review["key_id"]
            key_id_to_data_mapping[key_id] = review

    return {
        "cluster_data": final_output,
        "key_map": key_id_to_data_mapping,
        "result": res,
    }


def batch_node(llms: List[BaseChatModel]) -> Callable[[BatchInputState], GeneralState]:
    """Create a batch-processing graph node bound to a specific LLM model.
    Args:
        model_name: Name of the LLM model to use for batch processing.

    Returns:
        A callable graph node function
    """

    def llm_batch_node(state: BatchInputState) -> GeneralState:
        """Process a single batch using the configured LLM model.

        Args:
            state: Batch-specific state containing the batch content,
                batch index, and starting offset.

        Returns:
            A partial GeneralState containing the combined batch output.
        """

        llm = llms[state["batch_no"] % len(llms)]
        llm = llm.with_config(tags=["batch_run"])

        batch_result = batch_agent(llm, state["batch"])
        return {"combined_data": batch_result.model_dump()}

    return llm_batch_node


def cluster_node(llm: BaseChatModel) -> Callable[[GeneralState], GeneralState]:
    """Create a clustering graph node bound to a specific LLM model.

    Args:
        model_name: Name of the LLM model to use for clustering.

    Returns:
        A callable graph node function
    """

    def llm_cluster_node(state: GeneralState) -> GeneralState:
        """Cluster review titles into high-level themes using an LLM.

        Args:
            state: Current graph state containing cluster candidates
                and key-to-review mappings.

        Returns:
            A partial GeneralState update with the final themed output.
        """
        cluster_prompt = ""

        for i, title in enumerate(state["cluster_data"]):
            cluster_prompt += f"{i}: {title['title']}\n"

        resp = cluster_agent(llm, cluster_prompt).model_dump()

        final_data = []
        for cluster in resp["clusters"]:
            for member in cluster["members"]:
                for key_id in state["cluster_data"][member]["ids"]:
                    final_data.append(
                        {
                            "theme": cluster["cluster_title"],
                            **state["key_map"][key_id],
                        }
                    )

        return {"result": final_data}

    return llm_cluster_node


def data_ingestion_node(state: GeneralState) -> GeneralState:
    """Prepare token-limited review batches for downstream graph nodes.

    Args:
        state (GeneralState): Graph state containing the product identifier
            under the key ``product_id``.

    Returns:
        GeneralState: Updated state containing:
            - batches (list[dict]): A list of token-bounded review batches,
              each with ``start_idx`` and ``batch`` fields.
            - review_list (list[str]): The original list of reviews for the
              specified product.
    """

    def toklen(x):
        return len(tiktoken.encoding_for_model("gpt-4o").encode(x))

    review_list = review_dataset[state["product_id"]]["reviews"]
    batches = []
    sample_batch = ""
    rev_id = 1
    start_idx = 0
    for i, rev in enumerate(review_list):
        next_entry = f"rev id :{i}\nreview :{rev}\n\n"
        if toklen(sample_batch) + toklen(next_entry) + toklen(SYSTEM_PROMPT) > MAX_TOK:
            if sample_batch.strip():
                batches.append(
                    {
                        "start_idx": start_idx,
                        "batch": sample_batch,
                    }
                )
            sample_batch = ""
            rev_id = 1
            start_idx = i
            next_entry = f"rev id :{i}\nreview :{rev}\n\n"
        sample_batch += next_entry
        rev_id += 1
    if sample_batch.strip():
        batches.append(
            {
                "start_idx": start_idx,
                "batch": sample_batch,
            }
        )
    return {
        "batches": batches[:2],
        "review_list": review_list,
    }
