from typing import TypedDict, List, Annotated, Any
from .reducers import batch_reducer
from .types import ReviewDetails


class GeneralState(TypedDict):
    """Global graph state shared across all LangGraph nodes."""

    product_id: int
    """Index of the product in the dataset.

    This value is used to fetch the corresponding review list from
    the dataset. The index ranges from 0 to the total number of
    available products.
    """

    review_list: List[str]
    """Raw reviews associated with the selected product.

    Each entry in the list represents a single user review string.
    """

    batches: List[dict[int, str]]
    """Token-bounded batches of reviews.

    Each batch contains a concatenated string of multiple reviews and
    the index from which the batch starts in the original review list.

    Example:
        ```json
        {
            "start_idx": 0,
            "batch": "review 1: ... review 2: ..."
        }
        ```
    """

    combined_data: Annotated[List[ReviewDetails], batch_reducer]
    """Aggregated output from all batch-processing nodes.

    This field is updated using ``batch_reducer`` to merge results
    from multiple batch executions into a single list.
    """

    cluster_data: List[dict]
    """Intermediate clustering input.

    Contains normalized titles and their associated key identifiers,
    used as input for the clustering agent.
    """

    key_map: dict
    """Mapping from generated key IDs to their original review metadata.

    This allows clustered results to be traced back to the original
    review content and attributes.
    """

    result: Any
    """Final graph output.

    Holds the fully processed and clustered results produced at the
    end of the graph execution.
    """


class BatchInputState(TypedDict):
    """State passed to an individual batch-processing node."""

    batch_no: int
    """Sequential index of the batch.

    Used for routing, logging, or load-balancing across API keys.
    """

    batch: str
    """Concatenated review text for this batch.

    This string is passed directly to the batch LLM agent for processing.
    """

    start_idx: int
    """Starting index of the batch in the original review list.

    Enables downstream nodes to map batch results back to the source reviews.
    """
