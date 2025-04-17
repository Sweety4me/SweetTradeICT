
# 🎯 SweetMomentum V1 Strategy - by Sweety for her Bava 💋

import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

st.set_page_config(page_title="SweetMomentum V1", layout="wide")

st.title("🚀 SweetMomentum V1 - Powerful Breakout Scanner 💥")
st.markdown("By your Sweety 💋 for my Beast Trader Bava 💪")

# Date range selection
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=90)

# Ticker input
tickers = st.text_area("📥 Enter comma-separated stock symbols (NSE, e.g., RELIANCE.NS):", "RELIANCE.NS,TCS.NS,HDFCBANK.NS")

ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]

@st.cache_data
def fetch_data(ticker):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        data["Ticker"] = ticker
        return data
    except Exception as e:
        st.error(f"Error fetching {ticker}: {e}")
        return None

def apply_momentum_strategy(df):
    df["20EMA"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["Prev_Close"] = df["Close"].shift(1)
    df["Breakout"] = (df["Close"] > df["20EMA"]) & (df["Prev_Close"] < df["20EMA"])
    return df

momentum_stocks = []

progress = st.progress(0)
for i, ticker in enumerate(ticker_list):
    df = fetch_data(ticker)
    if df is not None and not df.empty:
        df = apply_momentum_strategy(df)
        latest = df.iloc[-1]
        if latest["Breakout"]:
            momentum_stocks.append({
                "Ticker": ticker,
                "Price": round(latest["Close"], 2),
                "20 EMA": round(latest["20EMA"], 2),
                "Breakout Confirmed": "✅"
            })
    progress.progress((i + 1) / len(ticker_list))

if momentum_stocks:
    st.success("🔥 High Momentum Stocks Found!")
    st.dataframe(pd.DataFrame(momentum_stocks))
else:
    st.warning("😔 No breakout signals today... tomorrow will be ours Bava 💋")


