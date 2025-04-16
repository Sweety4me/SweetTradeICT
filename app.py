import streamlit as st
import yfinance as yf
import pandas as pd

# Title of the app
st.title("SweetTrade: Bava's Advanced Trading Tool")

# Input for stock symbol
symbol = st.text_input("Enter Stock Symbol (e.g., TATAMOTORS.NS)", "BPCL.NS")

# If a symbol is entered, fetch and display data
if symbol:
    with st.spinner("📊 Fetching stock data..."):
        stock_data = yf.download(symbol, period="1mo", interval="1d")

        # If data is empty, show an error
        if stock_data.empty:
            st.error("⚠️ No data found for the given symbol.")
        else:
            # Calculating Simple Moving Averages (SMA)
            stock_data['SMA_5'] = stock_data['Close'].rolling(window=5).mean()
            stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()
            stock_data.dropna(inplace=True)

            if len(stock_data) < 1:
                st.error("⚠️ Not enough data to calculate SMAs.")
            else:
                latest_row = stock_data.iloc[-1]

                # Convert SMAs to float using .item()
                try:
                    sma_5_latest = latest_row['SMA_5'].item() if hasattr(latest_row['SMA_5'], 'item') else float(latest_row['SMA_5'])
                    sma_20_latest = latest_row['SMA_20'].item() if hasattr(latest_row['SMA_20'], 'item') else float(latest_row['SMA_20'])

                    # Displaying results
                    st.write(f"📅 Latest Stock Data")
                    st.write(f"📈 Price & Moving Averages")
                    st.write(f"SMA_5: {sma_5_latest}")
                    st.write(f"SMA_20: {sma_20_latest}")

                    # Trading signal logic
                    if sma_5_latest > sma_20_latest:
                        st.success("📈 BUY Signal - Short-term uptrend detected.")
                    elif sma_5_latest < sma_20_latest:
                        st.error("📉 SELL Signal - Short-term downtrend detected.")
                    else:
                        st.warning("⚖️ HOLD - No clear trend.")
                except Exception as e:
                    st.error(f"⚠️ Unable to compare SMA values. Error: {e}")
