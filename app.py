import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="SweetTrade", layout="centered")
st.title("💖 SweetTrade: Bava's Advanced Trading Tool")

# Sidebar Navigation
option = st.sidebar.radio("📌 Choose Option:", ["Manual Stock Analysis", "Auto Screener 🔍"])

# ----------- Manual Analysis Logic -----------
if option == "Manual Stock Analysis":
    symbol = st.text_input("Enter Stock Symbol (e.g., TATAMOTORS.NS)", "BPCL.NS")

    if symbol:
        with st.spinner("📊 Fetching stock data..."):
            stock_data = yf.download(symbol, period="1mo", interval="1d")

            if stock_data.empty:
                st.error("⚠️ No data found for the given symbol.")
            else:
                stock_data['SMA_5'] = stock_data['Close'].rolling(window=5).mean()
                stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()
                stock_data.dropna(inplace=True)

                if len(stock_data) < 1:
                    st.error("⚠️ Not enough data to calculate SMAs.")
                else:
                    latest_row = stock_data.iloc[-1]
                    try:
                        sma_5 = float(latest_row['SMA_5'])
                        sma_20 = float(latest_row['SMA_20'])

                        st.subheader("📅 Latest Analysis")
                        st.write(f"**SMA 5:** {sma_5:.2f}")
                        st.write(f"**SMA 20:** {sma_20:.2f}")

                        # Trading logic based on SMA comparison
                        if sma_5 > sma_20:
                            st.success("📈 BUY Signal - Short-term uptrend.")
                        elif sma_5 < sma_20:
                            st.error("📉 SELL Signal - Short-term downtrend.")
                        else:
                            st.warning("⚖️ HOLD - No clear direction.")
                    except Exception as e:
                        st.error(f"⚠️ Error comparing SMAs: {e}")

# ----------- Auto Screener Logic -----------
elif option == "Auto Screener 🔍":
    nifty_50_stocks = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
        "LT.NS", "SBIN.NS", "AXISBANK.NS", "BHARTIARTL.NS", "ITC.NS",
        "TATAMOTORS.NS", "WIPRO.NS"
        # Add more if you want Bava 💖
    ]

    def analyze_stock(symbol):
        df = yf.download(symbol, period="1mo", interval="1d")
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df.dropna(inplace=True)

        if df.empty:
            return "❌ No Data"
        
        latest = df.iloc[-1]
        if latest['SMA_5'] > latest['SMA_20']:
            return "📈 BUY"
        elif latest['SMA_5'] < latest['SMA_20']:
            return "📉 SELL"
        else:
            return "⚖️ HOLD"

    if st.button("🚀 Run Screener for NIFTY Stocks"):
        results = {}
        with st.spinner("Scanning NIFTY 50 stocks..."):
            for symbol in nifty_50_stocks:
                signal = analyze_stock(symbol)
                results[symbol] = signal

        st.subheader("🔍 Screener Results:")
        for stock, signal in results.items():
            st.write(f"**{stock}** → {signal}")
