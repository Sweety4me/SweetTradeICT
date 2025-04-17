import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# App title
st.set_page_config(page_title="SweetTrade - Manual Stock Analysis", layout="wide")
st.title("🍬 SweetTrade Manual Stock Analyzer")

# Input
ticker = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS):", value="RELIANCE.NS")

if ticker:
    try:
        # Fetch data
        df = yf.download(ticker, period="3mo", interval="1d")

        if df.empty:
            st.error("No data found. Please check the stock symbol.")
        elif df.shape[0] < 20:
            st.warning("Not enough data to calculate indicators (minimum 20 rows required).")
        else:
            # Calculate Indicators
            df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['SMA50'] = df['Close'].rolling(window=50).mean()

            # Display Table
            st.subheader("📊 Stock Data with Indicators")
            st.dataframe(df[['Close', 'RSI', 'SMA20', 'SMA50']].dropna().tail(30))

            # Plot Chart
            st.subheader("📈 Price Chart with Moving Averages")
            st.line_chart(df[['Close', 'SMA20', 'SMA50']])

            # Show RSI
            st.subheader("📉 RSI Trend")
            st.line_chart(df[['RSI']].dropna())
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
