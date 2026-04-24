import tempfile
import unittest
from pathlib import Path

from services.interview_bank import InterviewBank


class InterviewBankTests(unittest.TestCase):
    def test_seed_and_filter(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "interview.db"
            bank = InterviewBank(str(db_path))
            seeded = bank.seed_hot_roles()
            self.assertGreaterEqual(seeded, 1)

            all_rows = bank.list_questions()
            self.assertGreaterEqual(len(all_rows), 1)

            ai_rows = bank.list_questions(position="AI Engineer", difficulty="All")
            self.assertGreaterEqual(len(ai_rows), 1)


if __name__ == "__main__":
    unittest.main()
