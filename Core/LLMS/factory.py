from pathlib import Path
from typing import Dict, List
import json
import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openrouter import ChatOpenRouter


def _load_config() -> dict:
    """
    Loads Core/config.json regardless of execution directory.
    """
    core_path = Path(__file__).resolve().parents[1]
    config_path = core_path / "config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, "r") as f:
        return json.load(f)


def _load_keys():
    try:
        gemini_keys = json.loads(os.environ["GEMINI_KEY_COLLECTION"])
        groq_keys = json.loads(os.environ["GROQ_KEY_COLLECTION"])
        openrouter_keys = json.loads(os.environ["OPEN_ROUTER_KEY_COLLECTION"])
    except KeyError as e:
        raise EnvironmentError(f"Missing required environment variable: {str(e)}")

    return {
        "google": gemini_keys,
        "groq": groq_keys,
        "openrouter": openrouter_keys,
    }


def build_llm_factory() -> Dict[str, List]:
    """
    Builds and returns a dictionary:
    {
        "planner_llm": [ChatGroq(...), ...],
        "coder_llm_data_analysis": [...],
        ...
    }
    """

    config = _load_config()["LLM_CONFIG"]
    keys = _load_keys()

    llm_factory: Dict[str, List] = {}

    for llm_type, llm_config in config.items():
        provider = llm_config["provider"]
        model_name = llm_config["model_name"]
        temperature = llm_config["temprature"]
        key_ids = llm_config["key_ids"]

        llms = []

        for key_index in key_ids:
            api_key = keys[provider][key_index]

            if provider == "groq":
                llm = ChatGroq(
                    model=model_name,
                    api_key=api_key,
                    temperature=temperature,
                )

            elif provider == "openrouter":
                llm = ChatOpenRouter(
                    model=model_name,
                    api_key=api_key,
                    temperature=temperature,
                )

            elif provider == "google":
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    api_key=api_key,
                    temperature=temperature,
                )

            else:
                raise ValueError(f"Unsupported provider: {provider}")

            llms.append(llm)

        llm_factory[llm_type] = llms

    return llm_factory
