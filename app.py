import streamlit as st
import yfinance as yf
import pandas as pd

# — App Config —
st.set_page_config(page_title="SweetTrade ICT+SMC", layout="wide")
st.title("🍬 SweetTrade ICT+SMC Manual Analyzer")

# — Input —
ticker_input = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")
ticker = ticker_input.strip().upper()

if ticker:
    df = yf.download(ticker, period="3mo", interval="1d", progress=False)
    if df.empty or len(df) < 50:
        st.error("⚠️ Not enough data (need ≥50 daily candles).")
    else:
        # Flatten MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 1D Close Series
        close = df['Close'].astype(float)

        # Indicators
        df['SMA20'] = close.rolling(20).mean()
        df['SMA50'] = close.rolling(50).mean()
        df['EMA10'] = close.ewm(span=10, adjust=False).mean()
        df.dropna(subset=['SMA20', 'SMA50', 'EMA10'], inplace=True)

        # Latest values
        latest = df.iloc[-1]
        price = latest['Close']
        sma20 = latest['SMA20']
        sma50 = latest['SMA50']

        # Market Structure
        bullish = price > sma50
        bearish = price < sma50

        # Strategy Logic (Order‑Block style)
        if bullish and price > sma20:
            entry = price
            sl = sma50
            target = entry + (entry - sl) * 5  # 1:5 risk-reward
            outcome = "📈 BUY SETUP"
        elif bearish and price < sma20:
            entry = price
            sl = sma50
            target = entry - (sl - entry) * 5  # 1:5 risk-reward
            outcome = "📉 SELL SETUP"
        else:
            entry = sl = target = None
            outcome = "⚖️ NO CLEAR SETUP"

        # Determine follow-up guidance
        if entry:
            if price >= target:
                guidance = "🟢 Exit – Target Hit"
            elif price <= sl:
                guidance = "🔴 Exit – Stop‑Loss Hit"
            elif price >= entry * 1.02:  # Price 2% above entry to trail SL
                guidance = "🟡 Trail SL"
            else:
                guidance = "⚪ Hold"
        else:
            guidance = "⚪ No Setup"

        # Display Data & Indicators
        st.subheader(f"📊 Latest Data for {ticker}")
        st.write(df[['Close', 'SMA20', 'SMA50', 'EMA10']].tail(5))

        st.subheader("📈 Charts")
        st.line_chart(df[['Close', 'SMA20', 'SMA50']])

        # Display Strategy Signals and Guidance
        st.subheader("🎯 Strategy Signal")
        st.write(outcome)
        if entry:
            st.write(f"• Entry:  {entry:.2f}")
            st.write(f"• Stop‑Loss:  {sl:.2f}")
            st.write(f"• Target (1:5 RR):  {target:.2f}")
            st.write(f"🔍 Guidance: {guidance}")
