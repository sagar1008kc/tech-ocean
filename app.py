from tkinter import Image
import streamlit as st
from services.ai_chat import chat_with_llm
import yfinance as yf
import matplotlib.pyplot as plt

st.markdown(
    """
    <style>
    /* Center the main chat column */
    .chat-main {
        max-width: 800px;
        margin: 0 auto;
    }

    /* Make system messages subtle */
    .chat-system {
        color: #888;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    /* Optional: tweak user/assistant bubbles via Streamlit's classes */
    .stChatMessage {
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Tech Ocean")
tab1, tab2, tab3 = st.tabs(["👋 Welcome", "📈 Stock Explorer", "💬 Chatboot"])

# --- TAB 1: Simple UI ---
with tab1:
    st.subheader("Hello from Tech Ocean!")
    st.write("This app is built using only Python and Streamlit.")

    name = st.text_input("What is your name?")

    if name:
        st.success(f"Nice to meet you, {name}!")
    else:
        st.info("Type your name above to say hi.")


# --- TAB 2: Stock Explorer ---
with tab2:
    st.subheader("Explore stock prices")

    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Stock ticker (e.g., AAPL, MSFT, TSLA)", value="AAPL")
    with col2:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)

    if st.button("Load Stock Data"):
        if not ticker.strip():
            st.error("Please enter a ticker symbol.")
        else:
            data = yf.download(ticker, period=period, auto_adjust=True)
            if data.empty:
                st.error("No data found. Check the ticker symbol.")
            else:
                data.reset_index(inplace=True)

                st.write(f"Showing data for **{ticker.upper()}**")
                st.dataframe(data.tail())

                fig, ax = plt.subplots()
                ax.plot(data["Date"], data["Close"])
                ax.set_title(f"{ticker.upper()} Close Price ({period})")
                ax.set_xlabel("Date")
                ax.set_ylabel("Price")
                st.pyplot(fig)

# --- TAB 3: Chatbot ---
with tab3:
    st.markdown('<div class="chat-main">', unsafe_allow_html=True)
    st.subheader("💬 Tech Ocean Chat")

    # Initialize chat history if not there
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant focused on Python, data, and tech questions."
            }
        ]

    # Controls row: clear chat, info, etc.
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("🧹 Clear chat"):
            st.session_state["chat_messages"] = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant focused on Python, data, and tech questions."
                }
            ]
            st.rerun()   # ✅ use official API, no extra import
    with c3:
        st.caption("Running locally with Ollama 🧠")

    # Show chat history (skip system in visible UI)
    for msg in st.session_state["chat_messages"]:
        if msg["role"] == "system":
            continue
        elif msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    # Chat input always rendered at the bottom of this tab
    user_input = st.chat_input("Message Tech Ocean Bot...")

    if user_input:
        # 1) Add user message
        st.session_state["chat_messages"].append(
            {"role": "user", "content": user_input}
        )

        # 2) Display immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # 3) Get AI reply
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = chat_with_llm(st.session_state["chat_messages"])
                st.markdown(reply)

        # 4) Save assistant reply
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": reply}
        )

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; color: #888;">
        © 2025 Dr. SK — All Rights Reserved
    </div>
    """,
    unsafe_allow_html=True
)
