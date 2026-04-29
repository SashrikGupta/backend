from typing import TypedDict, List


class KeyPhraseData(TypedDict):
    """Structured information extracted for a single key phrase."""

    title: str
    """Normalized title or theme associated with the key phrase."""

    keyphrase: str
    """Exact key phrase extracted from the review text."""

    sentiment: int
    """Sentiment score for the key phrase.

    Typically expected to be in a bounded range
    (e.g., 1, 10 or 1–10 depending on the model).
    """

    rid: int
    """Review ID from which this key phrase was extracted."""

    key_id: int
    """Globally unique identifier assigned during post-processing.

    Used for clustering and reverse lookups.
    """


class ReviewData(TypedDict):
    """Collection of key phrases extracted from a single review."""

    review_data: List[KeyPhraseData]
    """List of extracted key phrase objects."""


class ReviewDetails(TypedDict):
    """Processed representation of a single review."""

    id: int
    """Unique identifier of the review."""

    review_data: List[KeyPhraseData]
    """Key phrase extraction results for this review."""
