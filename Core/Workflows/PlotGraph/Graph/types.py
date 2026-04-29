from typing import TypedDict


class Plot(TypedDict):
    path: str
    filename: str
    key_insights: str


class AnalysisData(TypedDict):
    theme: str
    title: str
    keyphrase: str
    rid: int
    key_id: int
