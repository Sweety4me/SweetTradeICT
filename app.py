import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# App Config
st.set_page_config(page_title="SweetTrade - Manual Stock Analyzer", layout="wide")
st.title("🍬 SweetTrade Manual Stock Analyzer")

# Input box
ticker = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS):", value="RELIANCE.NS")

if ticker:
    try:
        # Fetching data
        df = yf.download(ticker, period="3mo", interval="1d")

        if df.empty:
            st.error("No data found. Please check the stock symbol.")
        elif len(df) < 20:
            st.warning("Not enough data to calculate indicators (minimum 20 rows required).")
        else:
            # Fix: make sure we use the proper 1D Series
            close_series = df['Close']

            # Technical Indicators
            rsi = ta.momentum.RSIIndicator(close=close_series, window=14)
            df['RSI'] = rsi.rsi()

            df['SMA20'] = close_series.rolling(window=20).mean()
            df['SMA50'] = close_series.rolling(window=50).mean()

            # Show Table
            st.subheader("📊 Stock Data with Indicators")
            st.dataframe(df[['Close', 'RSI', 'SMA20', 'SMA50']].dropna().tail(30))

            # Charts
            st.subheader("📈 Price Chart with Moving Averages")
            st.line_chart(df[['Close', 'SMA20', 'SMA50']].dropna())

            st.subheader("📉 RSI Trend")
            st.line_chart(df[['RSI']].dropna())

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
