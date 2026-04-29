from .schemas import clusterOutput
from .prompt import SYSTEM_PROMPT, INSTRUCTION_PROMPT
from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage, SystemMessage


def cluster_agent(llm: BaseChatModel, context: str) -> clusterOutput:
    """
    Processes a titles to clusters

    Args:
        llm : BaseChatModel
        context : str

    Returns:
        clusterOutput : A structured object containing the model’s

    Raises:
        ValueError: If the model fails to generate output matching the
            `BatchReviewOutput` schema.
    """
    message_chain = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=INSTRUCTION_PROMPT + "\n\n" + context),
    ]

    struct_llm = llm.with_structured_output(clusterOutput)
    result = struct_llm.invoke(message_chain)
    return result
