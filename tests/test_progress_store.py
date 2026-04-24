import tempfile
import unittest
from pathlib import Path

from services.progress_store import ProgressStore


class ProgressStoreTests(unittest.TestCase):
    def test_profile_and_metrics_persist(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "progress.json"
            store = ProgressStore(str(file_path))

            store.update_profile(
                {
                    "goal": "Become better at Python",
                    "level": "beginner",
                    "pace_hours_per_week": 6,
                    "weak_topics": ["loops"],
                }
            )
            store.add_quiz_result(topic="python", score=0.8)
            store.set_milestones(["Finish week 1 tasks"])

            state = store.read()
            self.assertEqual(state["profile"]["goal"], "Become better at Python")
            self.assertEqual(state["quiz_history"][0]["topic"], "python")
            self.assertEqual(state["milestones"][0], "Finish week 1 tasks")


if __name__ == "__main__":
    unittest.main()
