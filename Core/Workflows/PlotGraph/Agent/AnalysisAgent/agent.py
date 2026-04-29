from langchain.messages import AIMessage
from langchain.chat_models import BaseChatModel
from .prompt import ANALYSER_PROMPT
from .schema import PlotList


def analysis_agent(
    llm: BaseChatModel,
    textual_data: str,
    dataset_info: str,
    dataset_eg: str,
    image_data: str,
    image_content: dict,
) -> AIMessage:
    formatted_analyser_text = ANALYSER_PROMPT.format_map(
        {
            "dataset_info": dataset_info,
            "dataset_eg": dataset_eg,
            "textual_data": textual_data,
            "image_data": image_data,
        }
    )
    message = {
        "role": "user",
        "content": [{"type": "text", "text": formatted_analyser_text}, *image_content],
    }
    plot_result = llm.with_structured_output(PlotList).invoke([message])

    return plot_result
