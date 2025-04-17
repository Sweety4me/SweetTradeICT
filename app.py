import yfinance as yf
import pandas as pd
import ta
import streamlit as st

# Example Symbols (You can input any symbol)
symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS)", "RELIANCE.NS")

# Fetch the data for the last month (15-minute candles)
df = yf.download(symbol, period="1mo", interval="15m")

# Calculate Simple Moving Averages (SMA) and Exponential Moving Averages (EMA)
df['SMA20'] = df['Close'].rolling(window=20).mean()
df['SMA50'] = df['Close'].rolling(window=50).mean()
df['EMA10'] = ta.trend.ema_indicator(df['Close'], window=10)

# Market Structure: Identify Bullish and Bearish Trend
df['bullish_structure'] = df['Close'] > df['SMA50']  # Bullish if above SMA50
df['bearish_structure'] = df['Close'] < df['SMA50']  # Bearish if below SMA50

# Define Buy and Sell Signals Based on Market Structure
df['buy_signal'] = (df['bullish_structure'] & (df['Close'] > df['SMA20']))
df['sell_signal'] = (df['bearish_structure'] & (df['Close'] < df['SMA20']))

# Display signals in Streamlit
st.title(f"SweetTrade: {symbol} - ICT + SMC Strategy Signals")

st.subheader("Buy Signals:")
st.write(df[df['buy_signal'] == True])

st.subheader("Sell Signals:")
st.write(df[df['sell_signal'] == True])

# Show price chart with indicators and signals
st.subheader(f"Price Chart with SMA20, SMA50, and Buy/Sell Signals")
st.line_chart(df[['Close', 'SMA20', 'SMA50']])

# Add More Advanced Concepts Later (Liquidity Pools, Order Block Patterns)
