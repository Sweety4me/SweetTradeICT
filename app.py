import streamlit as st
import yfinance as yf
import pandas as pd

# — App Config —
st.set_page_config(page_title="SweetTrade Manual Analyzer", layout="wide")
st.title("🍬 SweetTrade Manual Stock Analyzer")

# — Input —
ticker_input = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")
ticker = ticker_input.strip().upper()

if ticker:
    # Fetch 3 months of daily data
    df = yf.download(ticker, period="3mo", interval="1d", progress=False)

    # Handle empty or too‑small data
    if df.empty:
        st.error("❌ No data found. Check the symbol.")
    elif len(df) < 20:
        st.error("⚠️ Not enough data (need ≥20 rows).")
    else:
        # — Flatten multi‑level columns if they exist —
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # — Ensure Close is a proper 1D Series —
        close = df['Close'].astype(float)

        # — Calculate Indicators with pandas only —
        df['SMA20'] = close.rolling(window=20).mean()
        df['SMA50'] = close.rolling(window=50).mean()
        df['EMA10'] = close.ewm(span=10, adjust=False).mean()

        # — Drop rows that still have NaNs —
        df = df.dropna(subset=['SMA20','SMA50','EMA10'])

        # — Display last 30 rows of data with indicators —
        st.subheader("📊 Stock Data with SMA20, SMA50 & EMA10")
        st.dataframe(df[['Close','SMA20','SMA50','EMA10']].tail(30))

        # — Plot Price + Moving Averages —
        st.subheader("📈 Price Chart with SMA20, SMA50 & EMA10")
        st.line_chart(df[['Close','SMA20','SMA50','EMA10']])

