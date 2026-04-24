from __future__ import annotations

import json
from typing import Any, Dict, List

from services.llm_client import OllamaClient
from services.prompts import MODE_SYSTEM_PROMPTS, build_user_prompt
from services.rag_store import LocalRAGStore


class LearningOrchestrator:
    def __init__(self, llm_client: OllamaClient | None = None, rag_store: LocalRAGStore | None = None) -> None:
        self.llm_client = llm_client or OllamaClient()
        self.rag_store = rag_store or LocalRAGStore()

    def run(
        self,
        mode: str,
        user_input: str,
        model: str = "llama3.1",
        top_k: int = 3,
    ) -> Dict[str, Any]:
        retrieved = self.rag_store.retrieve(user_input, top_k=top_k)
        context = self._format_retrieved_context(retrieved)
        system_prompt = MODE_SYSTEM_PROMPTS.get(mode, MODE_SYSTEM_PROMPTS["mentor"])
        final_prompt = build_user_prompt(mode, user_input, context)

        response = self.llm_client.chat(
            messages=[{"role": "user", "content": final_prompt}],
            model=model,
            system_prompt=system_prompt,
        )

        parsed_payload = self._safe_json_loads(response)
        return {
            "mode": mode,
            "raw_response": response,
            "parsed": parsed_payload,
            "citations": [
                {"source_name": item["source_name"], "chunk_id": item["chunk_id"]}
                for item in retrieved
            ],
        }

    def _format_retrieved_context(self, items: List[Dict[str, str]]) -> str:
        if not items:
            return ""
        lines = []
        for item in items:
            lines.append(f"[source:{item['source_name']}#{item['chunk_id']}]")
            lines.append(item["text"])
            lines.append("")
        return "\n".join(lines).strip()

    def _safe_json_loads(self, content: str) -> Dict[str, Any] | None:
        trimmed = content.strip()
        if not trimmed.startswith("{"):
            return None
        try:
            parsed = json.loads(trimmed)
            if isinstance(parsed, dict):
                return parsed
            return None
        except json.JSONDecodeError:
            return None
