import unittest

from services.learning_orchestrator import LearningOrchestrator


class FakeClient:
    def __init__(self, response: str) -> None:
        self.response = response

    def chat(self, messages, model, system_prompt):
        return self.response


class FakeRag:
    def __init__(self):
        self.items = [
            {
                "chunk_id": "notes.md-0",
                "source_name": "notes.md",
                "text": "Python dictionaries map keys to values.",
            }
        ]

    def retrieve(self, query, top_k=3):
        return self.items[:top_k]


class LearningOrchestratorTests(unittest.TestCase):
    def test_returns_parsed_json_when_response_is_json(self):
        orchestrator = LearningOrchestrator(
            llm_client=FakeClient('{"topic":"python","difficulty":"beginner","questions":[]}'),
            rag_store=FakeRag(),
        )
        result = orchestrator.run(mode="quiz", user_input="quiz me on dicts")
        self.assertIsNotNone(result["parsed"])
        self.assertEqual(result["parsed"]["topic"], "python")
        self.assertEqual(len(result["citations"]), 1)

    def test_returns_raw_when_response_not_json(self):
        orchestrator = LearningOrchestrator(
            llm_client=FakeClient("Here is your explanation."),
            rag_store=FakeRag(),
        )
        result = orchestrator.run(mode="mentor", user_input="teach loops")
        self.assertIsNone(result["parsed"])
        self.assertIn("explanation", result["raw_response"].lower())


if __name__ == "__main__":
    unittest.main()
