from langchain.messages import HumanMessage, SystemMessage, AIMessage, AnyMessage
from langchain.chat_models import BaseChatModel
from .prompt import REPORTER_PROMPT
from typing import List


def reporter_agent(
    llm: BaseChatModel, messages: List[AnyMessage], user_query: str
) -> AIMessage:
    system_message = SystemMessage(
        content=REPORTER_PROMPT.format_map({"user_query": user_query})
    )
    print(system_message)
    messages = (
        [system_message]
        + messages
        + [
            HumanMessage(
                content="generate a nice explanation in markdown format from previous messages"
            )
        ]
    )
    return llm.invoke(messages)
