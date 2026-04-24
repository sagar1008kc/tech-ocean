from __future__ import annotations

from typing import Any, Dict, List


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaClient:
    def __init__(self, base_url: str = DEFAULT_OLLAMA_BASE_URL, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama3.1",
        system_prompt: str | None = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            import requests

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except ModuleNotFoundError:
            return "The `requests` package is not installed. Run `pip install -r requirements.txt`."
        except requests.exceptions.ConnectionError:
            return (
                "Could not connect to Ollama. Start the server with `ollama serve` "
                "and pull a model like `ollama pull llama3.1`."
            )
        except requests.exceptions.Timeout:
            return "Model response timed out. Try a shorter prompt or retry."
        except requests.exceptions.RequestException as exc:
            return f"Ollama request error: {exc}"

        try:
            data = response.json()
            return data["message"]["content"]
        except (ValueError, KeyError, TypeError):
            return f"Unexpected response from Ollama: {response.text[:300]}"
