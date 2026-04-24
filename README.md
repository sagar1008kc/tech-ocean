# AI Coach 2.0

A local-first Streamlit platform for students and professionals that combines:
- AI tutoring modes (mentor, quiz, practice, review, planner)
- Context-aware learning from uploaded files (RAG-lite)
- Personalized profile and progress tracking
- Stock/data exploration utilities already present in the original app

## Key Features
- **AI Learning Studio**
  - Explain Like Mentor
  - Quiz Me (JSON structured quiz output)
  - Practice Problems
  - Project Review
  - Study Plan Builder (JSON weekly plan)
- **RAG-lite context retrieval**
  - Upload `.txt`, `.md`, `.csv`
  - Local chunk indexing and retrieval
  - Source-aware context injection and citations
- **Personalization**
  - Learner profile (goal, level, pace, weak topics)
  - Quiz history trend
  - Milestone tracking from generated study plans
- **Data tools**
  - Premium AI Lab with mock interview generation and answer scoring
  - Hot positions interview collection (`AI Engineer`, `Fullstack Engineer`, etc.)
  - Persistent interview database using SQLite (`data/interview_bank.db`)
  - Downloadable interview collections and executive report exports

## Tech Stack
- Python 3.13
- Streamlit
- Ollama (local model inference)
- Pandas, NumPy
- Matplotlib
- yfinance
- requests
- SQLite (built-in, no external dependency)

## Installation
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

## Run
Start Ollama:
```bash
ollama serve
ollama pull llama3.1
```

Run the app:
```bash
streamlit run app.py
```

## Testing
```bash
python -m unittest discover -s tests
```

## Project Structure
```text
.
├── app.py
├── services/
│   ├── ai_chat.py
│   ├── llm_client.py
│   ├── prompts.py
│   ├── learning_orchestrator.py
│   ├── rag_store.py
│   └── progress_store.py
├── tests/
│   ├── test_learning_orchestrator.py
│   └── test_progress_store.py
├── requirements.txt
└── README.md
```

## Troubleshooting
- **Cannot connect to Ollama**: verify `ollama serve` is running.
- **Model not found**: run `ollama pull <model-name>` and use that model in the UI.
- **Empty RAG results**: upload files first and use prompts that reference uploaded content.
- **Interview collection missing**: open Premium AI Lab once to auto-seed hot role questions.

## License
MIT
