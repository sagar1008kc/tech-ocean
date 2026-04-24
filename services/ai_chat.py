from typing import Dict, List

from services.llm_client import OllamaClient


def chat_with_llm(messages: List[Dict[str, str]], model: str = "llama3.1") -> str:
    """
    Backward-compatible helper used by legacy chat tab.
    """
    system_messages = [m["content"] for m in messages if m.get("role") == "system"]
    chat_messages = [m for m in messages if m.get("role") != "system"]
    system_prompt = "\n\n".join(system_messages) if system_messages else None

    client = OllamaClient()
    return client.chat(messages=chat_messages, model=model, system_prompt=system_prompt)
