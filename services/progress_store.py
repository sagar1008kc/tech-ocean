from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List


class ProgressStore:
    def __init__(self, file_path: str = "data/learner_progress.json") -> None:
        self.path = Path(file_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(
                {
                    "profile": {
                        "goal": "",
                        "level": "beginner",
                        "pace_hours_per_week": 5,
                        "weak_topics": [],
                    },
                    "quiz_history": [],
                    "milestones": [],
                    "engagement": {
                        "xp": 0,
                        "streak_days": 0,
                        "last_active_date": "",
                    },
                    "session_log": [],
                }
            )

    def read(self) -> Dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def update_profile(self, profile: Dict[str, Any]) -> None:
        state = self.read()
        state["profile"] = profile
        self._write(state)

    def add_quiz_result(self, topic: str, score: float) -> None:
        state = self.read()
        history: List[Dict[str, Any]] = state.get("quiz_history", [])
        history.append({"topic": topic, "score": score})
        state["quiz_history"] = history[-30:]
        self._write(state)

    def set_milestones(self, milestones: List[str]) -> None:
        state = self.read()
        state["milestones"] = milestones
        self._write(state)

    def add_session_event(self, event_type: str, detail: str, xp_delta: int = 5) -> None:
        state = self.read()
        log: List[Dict[str, Any]] = state.get("session_log", [])
        log.append(
            {
                "event_type": event_type,
                "detail": detail,
                "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            }
        )
        state["session_log"] = log[-100:]
        engagement = state.get("engagement", {"xp": 0, "streak_days": 0, "last_active_date": ""})
        engagement["xp"] = int(engagement.get("xp", 0)) + xp_delta
        state["engagement"] = engagement
        self._write(state)

    def touch_daily_activity(self) -> Dict[str, Any]:
        state = self.read()
        engagement = state.get("engagement", {"xp": 0, "streak_days": 0, "last_active_date": ""})
        today_str = str(date.today())
        last_active_date = engagement.get("last_active_date", "")
        if last_active_date != today_str:
            new_streak = int(engagement.get("streak_days", 0)) + 1
            engagement["streak_days"] = new_streak
            engagement["last_active_date"] = today_str
            state["engagement"] = engagement
            self._write(state)
        return engagement

    def _write(self, data: Dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
