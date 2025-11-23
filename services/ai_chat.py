# services/ai_chat.py

import requests
from typing import List, Dict

OLLAMA_BASE_URL = "http://localhost:11434"


def chat_with_llm(messages: List[Dict[str, str]], model: str = "llama3.1") -> str:
    """
    Talk to a local Ollama model using its chat API.

    messages: list of dicts like:
      [{"role": "system"|"user"|"assistant", "content": "..."}, ...]

    model: the Ollama model name you pulled, e.g. "llama3.1"
    """

    # Separate system messages (for top-level `system` field) and the rest
    system_messages = [m["content"] for m in messages if m.get("role") == "system"]
    chat_messages = [m for m in messages if m.get("role") != "system"]

    # Build payload for Ollama
    payload: Dict[str, object] = {
        "model": model,
        "messages": chat_messages,
        "stream": False,
    }

    # If there are system messages, join them into one system prompt
    if system_messages:
        payload["system"] = "\n\n".join(system_messages)

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        # Common case: Ollama not running
        return (
            "⚠️ Could not connect to the local AI model.\n\n"
            "Make sure the Ollama server is running (run `ollama serve`) "
            "and that you have pulled the model:\n\n"
            "`ollama pull llama3.1`"
        )
    except requests.exceptions.Timeout:
        return "⚠️ The local AI model took too long to respond. Please try again."
    except requests.exceptions.RequestException as e:
        # Any other HTTP / request error
        return f"⚠️ Error talking to local AI model: {e}"

    # Parse Ollama response
    try:
        data = resp.json()
    except ValueError:
        return f"⚠️ Could not parse response from Ollama: {resp.text[:300]}"

    # Expected format:
    # {
    #   "model": "...",
    #   "created_at": "...",
    #   "message": {"role": "assistant", "content": "..."},
    #   "done": true,
    #   ...
    # }
    try:
        return data["message"]["content"]
    except (KeyError, TypeError):
        return f"⚠️ Unexpected response from Ollama: {data}"
