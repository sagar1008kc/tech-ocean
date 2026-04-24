from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List


class InterviewBank:
    def __init__(self, db_path: str = "data/interview_bank.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interview_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    question TEXT NOT NULL,
                    ideal_points TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'manual'
                )
                """
            )
            conn.commit()

    def add_question(
        self,
        position: str,
        difficulty: str,
        question: str,
        ideal_points: str,
        source: str = "manual",
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO interview_questions (position, difficulty, question, ideal_points, source)
                VALUES (?, ?, ?, ?, ?)
                """,
                (position, difficulty, question, ideal_points, source),
            )
            conn.commit()

    def list_questions(self, position: str = "All", difficulty: str = "All") -> List[Dict[str, str]]:
        clauses = []
        params: List[str] = []
        if position != "All":
            clauses.append("position = ?")
            params.append(position)
        if difficulty != "All":
            clauses.append("difficulty = ?")
            params.append(difficulty)

        where_clause = ""
        if clauses:
            where_clause = "WHERE " + " AND ".join(clauses)

        query = (
            "SELECT id, position, difficulty, question, ideal_points, source "
            f"FROM interview_questions {where_clause} ORDER BY id DESC"
        )
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "id": row[0],
                "position": row[1],
                "difficulty": row[2],
                "question": row[3],
                "ideal_points": row[4],
                "source": row[5],
            }
            for row in rows
        ]

    def seed_hot_roles(self) -> int:
        existing = self.list_questions()
        if existing:
            return 0

        seed_items = [
            ("AI Engineer", "Medium", "How would you design a RAG pipeline for production?", "Chunking strategy, embedding choice, retrieval quality checks, fallback logic.", "seed"),
            ("AI Engineer", "Hard", "How do you monitor and reduce hallucinations in LLM apps?", "Grounded prompts, retrieval citations, eval benchmarks, human review loop.", "seed"),
            ("Fullstack Engineer", "Medium", "How do you structure a scalable fullstack app?", "Clear API boundaries, shared contracts, state management, observability.", "seed"),
            ("Fullstack Engineer", "Hard", "How do you optimize performance from DB to frontend?", "Indexes/caching, pagination, API batching, client render optimization.", "seed"),
            ("Backend Engineer", "Medium", "How would you design an idempotent payment webhook handler?", "Idempotency keys, durable store, retries, dead-letter handling.", "seed"),
            ("Data Engineer", "Medium", "How do you build a reliable batch + streaming pipeline?", "Schema evolution, backfills, data quality, monitoring/alerts.", "seed"),
            ("ML Engineer", "Hard", "How do you handle model drift in production?", "Drift detection, retraining triggers, shadow deployments, rollback.", "seed"),
            ("DevOps Engineer", "Medium", "How do you implement zero-downtime deployments?", "Blue/green or canary strategy, health checks, rollback automation.", "seed"),
        ]
        for item in seed_items:
            self.add_question(*item)
        return len(seed_items)
