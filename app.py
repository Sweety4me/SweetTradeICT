import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# — App Config —
st.set_page_config(page_title="SweetTrade Manual Analyzer", layout="wide")
st.title("🍬 SweetTrade Manual Stock Analyzer")

# — Input —
ticker_input = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS):", value="RELIANCE.NS")
ticker = ticker_input.strip().upper()

if ticker:
    try:
        # — Fetch Data —
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)

        # — Early exits —
        if df.empty:
            st.error("No data found. Check symbol.")
        elif len(df) < 20:
            st.warning("Need at least 20 rows of data.")
        else:
            # — Flatten any MultiIndex columns down to their first level —
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # — Work with a true 1‑D Series for Close —
            close = df["Close"].astype(float)

            # — Calculate Indicators —
            df["RSI"]   = ta.momentum.RSIIndicator(close=close, window=14).rsi()
            df["SMA20"] = close.rolling(20).mean()
            df["SMA50"] = close.rolling(50).mean()

            # — Table of last 30 rows —
            st.subheader("📊 Stock Data with Indicators")
            display_df = df[["Close","RSI","SMA20","SMA50"]].dropna().tail(30)
            st.dataframe(display_df)

            # — Price + SMAs chart —
            st.subheader("📈 Price Chart with SMA20 & SMA50")
            st.line_chart(display_df[["Close","SMA20","SMA50"]])

            # — RSI chart —
            st.subheader("📉 RSI Indicator")
            st.line_chart(display_df[["RSI"]])

    except Exception as e:
        st.error(f"An error occurred: {e}")
