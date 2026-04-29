import traceback
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
from langchain.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class ToolArgs(BaseModel):
    code: str = Field(description="Python code to execute")


@tool(args_schema=ToolArgs)
def python(code: str, config: RunnableConfig) -> dict:
    """
    Executes Python code and returns execution results.
    python_env is injected at runtime via config.
    """
    python_env = config["configurable"]["python_env"]
    return python_env.run_code(code)


tools = [python]


def sandbox_code_agent(llm: BaseChatModel, max_retries: int = 5):
    def llm_code_agent(state: MessagesState, config: RunnableConfig):
        attempt = 0
        last_exception = None
        while attempt < max_retries:
            try:
                attempt += 1
                print(f"[sandbox_code_agent] Attempt {attempt}/{max_retries}")
                bound_llm = llm.bind_tools(tools)
                response = bound_llm.invoke(state["messages"])
                return {"messages": response}
            except Exception as e:
                last_exception = e
                print(f"[sandbox_code_agent] Retry {attempt} failed.")
                traceback.print_exc()
                if attempt >= max_retries:
                    raise RuntimeError(
                        f"sandbox_code_agent failed after {max_retries} attempts"
                    ) from last_exception
        raise RuntimeError("Unexpected failure in sandbox_code_agent")

    return llm_code_agent


def get_sandbox_graph(llm: BaseChatModel):

    builder = StateGraph(MessagesState)

    builder.add_node("sandbox_code_agent", sandbox_code_agent(llm))
    builder.add_node("python", ToolNode(tools))

    builder.add_edge(START, "sandbox_code_agent")

    builder.add_conditional_edges(
        "sandbox_code_agent",
        tools_condition,
        {
            "tools": "python",
            "__end__": END,
        },
    )

    builder.add_edge("python", "sandbox_code_agent")

    return builder.compile()
