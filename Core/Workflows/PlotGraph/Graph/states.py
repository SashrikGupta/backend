from typing import List, TypedDict
from .types import AnalysisData, Plot


class PlotAgent_InputState(TypedDict):
    run_id: int
    product_id: int
    query: str
    analysis_result: List[AnalysisData]
    graph_context: str


class PlotAgent_OutputState(TypedDict):
    graphical_plots: List[Plot]
    graphical_insight: str
