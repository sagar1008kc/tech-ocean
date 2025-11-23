📊 Tech Ocean — Python Data + Local AI Chat App

A simple multi-tab Streamlit application featuring:

👋 A friendly welcome UI

📈 Stock Explorer using yfinance

🤖 Local AI Chatbot powered by Ollama (llama3.1)

🎨 Clean UI styling + session-based chat history

🚀 Live Features

Stock Explorer — fetch historical stock data, auto-adjust, visualize using Matplotlib.

Local AI Chatbot — uses Ollama running locally (llama3.1) for offline AI responses.

Beautiful UI — custom CSS + Streamlit chat components.

🧰 Tech Stack

Python 3.13

Streamlit

Ollama (local model inference)

yfinance

matplotlib

requests

📦 Installation
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt

▶️ Run the App

Start Ollama first:

ollama serve
# and ensure model is pulled
ollama pull llama3.1


Then run Streamlit:

streamlit run app.py

📁 Project Structure
.
├── app.py                  # Main Streamlit UI
├── services/
│   └── ai_chat.py          # Ollama chat integration
├── requirements.txt
└── README.md

🔗 Useful Links

Ollama Chat API Docs — https://github.com/ollama/ollama/blob/main/docs/api.md

Streamlit Documentation — https://docs.streamlit.io

yfinance Documentation — https://pypi.org/project/yfinance/

Matplotlib — https://matplotlib.org/stable/contents.html

📝 License

MIT — free to use, modify, and share.

✨ Author

Dr. SK (Tech Ocean)
Sharing Python, AI, DSA & Tech learning:
