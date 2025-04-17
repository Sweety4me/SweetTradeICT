import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import ta

st.set_page_config(page_title="SweetTradeICT", layout="wide")

st.sidebar.title("🎬 Movie AI TOOLS")
st.sidebar.markdown("## Choose Option:")
option = st.sidebar.radio("📌 Choose Option:", ("Manual Stock Analysis", "Auto Screener 🔍"))

st.markdown("<h1 style='color:#1954ed;'>💖⚡ SweetTrade: Bava's Advanced Trading Tool</h1>", unsafe_allow_html=True)

nifty_stocks = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'LT.NS',
    'SBIN.NS', 'AXISBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'TATAMOTORS.NS', 'WIPRO.NS'
]

def calculate_indicators(stock):
    df = yf.download(stock, period="6mo", interval="1d", progress=False)
    df.dropna(inplace=True)

    # Technical Indicators
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['Signal'] = macd.macd_signal()
    df['EMA200'] = ta.trend.EMAIndicator(close=df['Close'], window=200).ema_indicator()

    latest = df.iloc[-1]
    signal = ""
    reason = []

    # Buy/Sell Logic
    if latest['RSI'] < 40:
        reason.append(f"RSI: {latest['RSI']:.0f}")
    elif latest['RSI'] > 70:
        reason.append(f"Overbought (RSI: {latest['RSI']:.0f})")

    if latest['MACD'] > latest['Signal']:
        reason.append("MACD: Bullish")
    else:
        reason.append("MACD: Bearish")

    if latest['Close'] > latest['EMA200']:
        reason.append("Above EMA200")
    else:
        reason.append("Below EMA200")

    if latest['RSI'] < 40 and latest['MACD'] > latest['Signal'] and latest['Close'] > latest['EMA200']:
        signal = "📈 BUY"
    elif latest['RSI'] > 70 and latest['MACD'] < latest['Signal'] and latest['Close'] < latest['EMA200']:
        signal = "📉 SELL"
    else:
        signal = "⚠️ HOLD"

    return signal, ", ".join(reason)

if option == "Auto Screener 🔍":
    if st.button("🚀 Run Screener for NIFTY Stocks"):
        results = []
        for stock in nifty_stocks:
            signal, reason = calculate_indicators(stock)
            results.append((stock, signal, reason))

        st.subheader("🔍 Screener Results:")
        for stock, signal, reason in results:
            st.markdown(f"**{stock}** → {signal} ({reason})")
