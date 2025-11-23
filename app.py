import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Python Data App", layout="wide")

st.title("📊 Python Data App (Pure Python + Browser UI)")

tab1, tab2 = st.tabs(["👋 Welcome", "📈 Stock Explorer"])

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
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; color: #888;">
        © 2025 Dr. SK — All Rights Reserved
    </div>
    """,
    unsafe_allow_html=True
)
