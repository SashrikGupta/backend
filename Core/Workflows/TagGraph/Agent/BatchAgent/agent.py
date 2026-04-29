from .schemas import BatchReviewOutput
from .prompt import SYSTEM_PROMPT, INSTRUCTION_PROMPT
from langchain.chat_models import BaseChatModel
from langchain.messages import HumanMessage, SystemMessage


def batch_agent(llm: BaseChatModel, context: str) -> BatchReviewOutput:
    """
    Processes a batch of input data using a chat-based LLM and returns
    a structured batch review output.

    Args:
        llm : BaseChatModel
        context : str

    Returns:
        BatchReviewOutput: A structured object containing the model's

    Raises:
        ValueError: If the model fails to generate output matching the
            `BatchReviewOutput` schema.
    """
    message_chain = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=INSTRUCTION_PROMPT + "\n\n" + context),
    ]

    struct_llm = llm.with_structured_output(BatchReviewOutput)
    result = struct_llm.invoke(message_chain)
    return result
