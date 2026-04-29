from langchain.messages import AIMessage
from langchain.chat_models import BaseChatModel
from .prompt import SUPERVISOR_PROMPT


def supervisor_agent(llm: BaseChatModel, prompt: str) -> AIMessage:
    return llm.invoke(SUPERVISOR_PROMPT.format_map({"query": prompt}))
