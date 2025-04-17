import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# — App Config —
st.set_page_config(page_title="SweetTrade - Manual Analyzer", layout="wide")
st.title("🍬 SweetTrade Manual Stock Analyzer")

# — Input —
ticker_input = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS):", value="RELIANCE.NS")
ticker = ticker_input.strip().upper()

if ticker:
    try:
        # — Fetch Data —
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)

        # — Handle empty or too-small data —
        if df.empty:
            st.error("No data found. Please check the stock symbol.")
        elif len(df) < 20:
            st.warning("Not enough data to calculate indicators (need ≥ 20 rows).")
        else:
            # — Flatten columns if MultiIndex —
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # — Ensure we have a 1D Close series —
            close = df['Close'].astype(float)

            # — Calculate Indicators —
            df['RSI']   = ta.momentum.RSIIndicator(close=close, window=14).rsi()
            df['SMA20'] = close.rolling(window=20).mean()
            df['SMA50'] = close.rolling(window=50).mean()

            # — Display Table —
            st.subheader("📊 Stock Data with Indicators")
            st.dataframe(
                df[['Close', 'RSI', 'SMA20', 'SMA50']]
                  .dropna()
                  .tail(30)
            )

            # — Price + MAs Chart —
            st.subheader("📈 Price Chart with SMA20 & SMA50")
            st.line_chart(
                df[['Close', 'SMA20', 'SMA50']].dropna()
            )

            # — RSI Chart —
            st.subheader("📉 RSI Indicator")
            st.line_chart(
                df[['RSI']].dropna()
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
