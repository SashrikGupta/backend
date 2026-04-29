from .states import MainState
from typing import Callable, List
from .tools import check_product


def base_router(target_node : List[str]) -> Callable[[MainState], str]:
    def router_node(state: MainState) -> str:
        if check_product(state["product_id"]):
            return target_node[0]
        else:
            return target_node[1]
    return router_node