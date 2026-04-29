from langgraph.graph import MessagesState


class MainState(MessagesState):
    run_id: int | None
    product_id: int = -1
    review_analysis: dict = {}
    plan: dict = {}
    current_sequence: int = -1
    user_query: str
    chain_start: int
