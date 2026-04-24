from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from io import StringIO
from typing import Dict, List, Tuple


WORD_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass
class ChunkRecord:
    chunk_id: str
    source_name: str
    text: str
    token_counts: Counter


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in WORD_RE.findall(text)]


def _cosine_similarity(vec_a: Counter, vec_b: Counter) -> float:
    if not vec_a or not vec_b:
        return 0.0

    dot = sum(vec_a[token] * vec_b[token] for token in vec_a if token in vec_b)
    mag_a = math.sqrt(sum(value * value for value in vec_a.values()))
    mag_b = math.sqrt(sum(value * value for value in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class LocalRAGStore:
    def __init__(self) -> None:
        self._chunks: List[ChunkRecord] = []

    def add_document(self, filename: str, raw_content: bytes) -> int:
        text = self._decode_file(filename, raw_content)
        chunks = self._chunk_text(text)
        base_index = len(self._chunks)
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{filename}-{base_index + idx}"
            self._chunks.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    source_name=filename,
                    text=chunk,
                    token_counts=Counter(_tokenize(chunk)),
                )
            )
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        query_vec = Counter(_tokenize(query))
        scored: List[Tuple[float, ChunkRecord]] = []
        for record in self._chunks:
            scored.append((_cosine_similarity(query_vec, record.token_counts), record))

        top = sorted(scored, key=lambda item: item[0], reverse=True)[:top_k]
        results: List[Dict[str, str]] = []
        for score, record in top:
            if score <= 0:
                continue
            results.append(
                {
                    "chunk_id": record.chunk_id,
                    "source_name": record.source_name,
                    "text": record.text,
                }
            )
        return results

    def chunk_count(self) -> int:
        return len(self._chunks)

    def _decode_file(self, filename: str, raw_content: bytes) -> str:
        if filename.lower().endswith(".csv"):
            try:
                import pandas as pd

                frame = pd.read_csv(StringIO(raw_content.decode("utf-8", errors="ignore")))
                return frame.to_csv(index=False)
            except ModuleNotFoundError:
                return raw_content.decode("utf-8", errors="ignore")
        return raw_content.decode("utf-8", errors="ignore")

    def _chunk_text(self, text: str, chunk_size: int = 900) -> List[str]:
        cleaned = text.strip()
        if not cleaned:
            return []
        return [cleaned[i : i + chunk_size] for i in range(0, len(cleaned), chunk_size)]
