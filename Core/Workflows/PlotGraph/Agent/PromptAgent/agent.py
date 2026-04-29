from langchain.messages import HumanMessage, SystemMessage, AIMessage
from langchain.chat_models import BaseChatModel
from .prompt import PROMPTER_INSTRUCTION_PROMPT, PROMPTER_SYSTEM_PROMPT


def prompt_agent(
    llm: BaseChatModel, dataset_info: str, dataset_eg: str, query: str
) -> AIMessage:
    system_prompt = PROMPTER_SYSTEM_PROMPT
    instruction_prompt = PROMPTER_INSTRUCTION_PROMPT.format_map(
        {"dataset_info": dataset_info, "dataset_eg": dataset_eg, "query": query}
    )
    messages = [SystemMessage(system_prompt), HumanMessage(instruction_prompt)]

    return llm.invoke(messages)
