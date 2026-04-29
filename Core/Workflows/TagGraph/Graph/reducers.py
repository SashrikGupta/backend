from typing import List
from .types import ReviewDetails, ReviewData


def batch_reducer(
    existing: List[ReviewDetails] | None,
    new_data: ReviewData,
) -> List[ReviewDetails]:
    """Accumulate batch-level review extraction results into the global state.

    Args:
        existing: Previously accumulated review results from earlier batches.
            This may be ``None`` when the reducer is invoked for the first time.
        new_data: Output produced by a single batch node containing extracted
            review data and associated key phrases.

    Returns:
        A list of consolidated review details with review IDs embedded in
        each key phrase entry.
    """
    if not existing:
        existing = []

    for review in new_data["reviews"]:
        for d in review["review_data"]:
            d["rid"] = review["id"]

        existing.append(
            {
                "id": review["id"],
                "review_data": review["review_data"],
            }
        )

    return existing
