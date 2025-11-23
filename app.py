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
st.set_page_config(page_title="TechOcean")
st.title("Tech Ocean")
tab1, tab2, tab3, tab4, tab5 = st.tabs([" Welcome", " Stock Explorer", "Analytics", "Data Lab", " Chatboot",])

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

# --- TAB 4: Pro Analytics ---
with tab3:
    st.subheader("📊 Advanced Stock Analytics")

    col1, col2, col3 = st.columns(3)
    with col1:
        pro_ticker = st.text_input("Stock ticker", value="AAPL", key="pro_ticker")
    with col2:
        pro_period = st.selectbox(
            "Period",
            ["3mo", "6mo", "1y", "2y", "5y"],
            index=2,
            key="pro_period",
        )
    with col3:
        interval = st.selectbox(
            "Interval",
            ["1d", "1wk", "1mo"],
            index=0,
            key="pro_interval",
        )

    if st.button("Run Analysis"):
        if not pro_ticker.strip():
            st.error("Please enter a ticker symbol.")
        else:
            data = yf.download(
                pro_ticker,
                period=pro_period,
                interval=interval,
                auto_adjust=True,
                progress=False,
            )
            if data.empty:
                st.error("No data found. Check the ticker symbol.")
            else:
                data["SMA20"] = data["Close"].rolling(window=20).mean()
                data["SMA50"] = data["Close"].rolling(window=50).mean()

                # Bollinger Bands (20-period, 2 std)
                rolling_mean = data["Close"].rolling(window=20).mean()
                rolling_std = data["Close"].rolling(window=20).std()
                data["BB_upper"] = rolling_mean + 2 * rolling_std
                data["BB_lower"] = rolling_mean - 2 * rolling_std

                # Returns
                data["Daily_Return"] = data["Close"].pct_change()
                data["Cumulative_Return"] = (1 + data["Daily_Return"]).cumprod() - 1

                st.write(f"### {pro_ticker.upper()} — Raw & Derived Data")
                st.dataframe(data.tail())

                # Price + SMA + Bollinger
                st.write("#### Price with Moving Averages & Bollinger Bands")
                fig, ax = plt.subplots()
                ax.plot(data.index, data["Close"], label="Close")
                ax.plot(data.index, data["SMA20"], label="SMA20")
                ax.plot(data.index, data["SMA50"], label="SMA50")
                ax.plot(data.index, data["BB_upper"], linestyle="--", label="BB Upper")
                ax.plot(data.index, data["BB_lower"], linestyle="--", label="BB Lower")
                ax.set_xlabel("Date")
                ax.set_ylabel("Price")
                ax.legend()
                st.pyplot(fig)

                # Cumulative return
                st.write("#### Cumulative Return")
                fig2, ax2 = plt.subplots()
                ax2.plot(data.index, data["Cumulative_Return"])
                ax2.set_xlabel("Date")
                ax2.set_ylabel("Cumulative Return")
                st.pyplot(fig2)
# --- TAB 4: Data Lab ---
with tab4:
    st.subheader("📂 Data Lab — Upload & Explore CSV")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        import pandas as pd

        df = pd.read_csv(uploaded_file)

        st.write("### Preview")
        st.dataframe(df.head())

        st.write("### Summary Statistics")
        st.write(df.describe(include="all"))

        # Choose numeric column to plot
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        if numeric_cols:
            col = st.selectbox("Select a numeric column to plot", numeric_cols)
            fig, ax = plt.subplots()
            ax.plot(df[col])
            ax.set_title(col)
            st.pyplot(fig)
        else:
            st.info("No numeric columns found to plot.")

        # Simple row filter
        st.write("### Filter Rows")
        st.write("Use this to see top N rows.")
        n = st.slider("Number of rows", min_value=5, max_value=min(100, len(df)), value=10)
        st.dataframe(df.head(n))
    else:
        st.info("Upload a CSV file to get started.")
# --- TAB 5: Chatbot ---
with tab5:
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
