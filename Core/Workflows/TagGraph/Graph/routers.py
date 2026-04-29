from langgraph.types import Send
from .states import GeneralState
from typing import List


def spawn_batches(
    state: GeneralState,
    *,
    target_node: str,
) -> List[Send]:
    """Create Send instructions for each batch in the graph state.

    Splits the precomputed batches in the state into individual `Send`
    messages targeting the specified LangGraph node.

    Args:
        state: Current graph state containing a `batches` entry.
        target_node: Name of the graph node to send each batch to.

    Returns:
        A list of `Send` objects, one per batch.
    """
    batches = state["batches"]
    sends = []

    for i, b in enumerate(batches):
        sends.append(
            Send(
                target_node,
                {
                    "batch_no": i,
                    "batch": b["batch"],
                    "start_idx": b["start_idx"],
                },
            )
        )

    return sends
