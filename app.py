import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import timedelta

# — App Config —
st.set_page_config(page_title="SweetTrade Pro", layout="wide")
st.title("🚀 SweetTrade Pro: ICT+SMC Manual, Intraday, Swing & Backtest")

# — Sidebar Modes —
mode = st.sidebar.radio("🔍 Choose Mode:",
    ["Manual Analysis", "Intraday Signals", "Swing Signals", "5Y Backtest"])

# — Helper Functions —  
def get_df(symbol, period, interval):
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

def manual_analyze(df, symbol):
    close = df['Close'].astype(float)
    df['SMA20'] = close.rolling(20).mean()
    df['SMA50'] = close.rolling(50).mean()
    df['EMA10'] = close.ewm(span=10, adjust=False).mean()
    df.dropna(subset=['SMA20','SMA50','EMA10'], inplace=True)

    latest = df.iloc[-1]
    price, sma20, sma50 = latest['Close'], latest['SMA20'], latest['SMA50']
    bullish, bearish = price > sma50, price < sma50

    if bullish and price > sma20:
        entry, sl = price, sma50
        target = entry + (entry - sl) * 5
        outcome = "📈 BUY SETUP"
    elif bearish and price < sma20:
        entry, sl = price, sma50
        target = entry - (sl - entry) * 5
        outcome = "📉 SELL SETUP"
    else:
        entry = sl = target = None
        outcome = "⚖️ NO CLEAR SETUP"

    # guidance
    if entry:
        if price >= target: guidance = "🟢 Exit – Target Hit"
        elif price <= sl:    guidance = "🔴 Exit – Stop‑Loss Hit"
        elif bullish and price >= entry * 1.02: guidance = "🟡 Trail SL"
        else:                guidance = "⚪ Hold"
    else:
        guidance = "⚪ No Setup"

    st.subheader(f"📊 Latest Data for {symbol}")
    st.dataframe(df[['Close','SMA20','SMA50','EMA10']].tail(5))
    st.subheader("📈 Charts")
    st.line_chart(df[['Close','SMA20','SMA50']])
    st.subheader("🎯 Strategy Signal")
    st.write(outcome)
    if entry:
        st.write(f"• Entry:    {entry:.2f}")
        st.write(f"• Stop‑Loss: {sl:.2f}")
        st.write(f"• Target:    {target:.2f}")
        st.info(f"🔍 Guidance: {guidance}")

def intraday_signals(df, symbol):
    close = df['Close']
    df['EMA9'] = close.ewm(span=9, adjust=False).mean()
    latest = df.iloc[-1]
    price, ema9 = latest['Close'], latest['EMA9']
    if price > ema9:
        signal = "📈 BUY"
        sl = ema9
        target = price + (price - sl) * 5
    elif price < ema9:
        signal = "📉 SELL"
        sl = ema9
        target = price - (sl - price) * 5
    else:
        signal = "⚖️ HOLD"
        sl = target = None

    # guidance
    if signal.startswith("📈"):
        if price >= target: guidance = "🟢 Exit – Target Hit"
        elif price <= sl:    guidance = "🔴 Exit – Stop‑Loss Hit"
        elif price >= price * 1.02: guidance = "🟡 Trail SL"
        else:                guidance = "⚪ Hold"
    elif signal.startswith("📉"):
        if price <= target: guidance = "🟢 Exit – Target Hit"
        elif price >= sl:    guidance = "🔴 Exit – Stop‑Loss Hit"
        elif price <= price * 0.98: guidance = "🟡 Trail SL"
        else:                guidance = "⚪ Hold"
    else:
        guidance = "⚪ Hold"

    st.success(f"{symbol} → {signal}")
    st.write(f"• Entry:    {price:.2f}")
    st.write(f"• Stop‑Loss: {sl:.2f}" if sl else "")
    st.write(f"• Target:    {target:.2f}" if target else "")
    st.info(f"🔍 Guidance: {guidance}")
    st.line_chart(df[['Close','EMA9']])

def swing_signals(df, symbol):
    close = df['Close']
    df['SMA5']  = close.rolling(5).mean()
    df['SMA20'] = close.rolling(20).mean()
    df.dropna(inplace=True)
    latest = df.iloc[-1]
    price, sma5, sma20 = latest['Close'], latest['SMA5'], latest['SMA20']
    if sma5 > sma20:
        signal = "📈 BUY"
        sl = sma20
        target = price + (price - sl) * 5
    elif sma5 < sma20:
        signal = "📉 SELL"
        sl = sma20
        target = price - (sl - price) * 5
    else:
        signal = "⚖️ HOLD"
        sl = target = None

    # guidance
    if signal.startswith("📈"):
        if price >= target: guidance = "🟢 Exit – Target Hit"
        elif price <= sl:    guidance = "🔴 Exit – Stop‑Loss Hit"
        elif price >= price * 1.02: guidance = "🟡 Trail SL"
        else:                guidance = "⚪ Hold"
    elif signal.startswith("📉"):
        if price <= target: guidance = "🟢 Exit – Target Hit"
        elif price >= sl:    guidance = "🔴 Exit – Stop‑Loss Hit"
        elif price <= price * 0.98: guidance = "🟡 Trail SL"
        else:                guidance = "⚪ Hold"
    else:
        guidance = "⚪ Hold"

    st.success(f"{symbol} → {signal}")
    st.write(f"• Entry:    {price:.2f}")
    st.write(f"• Stop‑Loss: {sl:.2f}" if sl else "")
    st.write(f"• Target:    {target:.2f}" if target else "")
    st.info(f"🔍 Guidance: {guidance}")
    st.line_chart(df[['Close','SMA5','SMA20']])

def backtest(symbol):
    df = get_df(symbol, "5y", "1d")
    df['SMA5']  = df['Close'].rolling(5).mean()
    df['SMA20'] = df['Close'].rolling(20).mean()
    df.dropna(inplace=True)
    trades = []
    for i in range(1, len(df)-1):
        prev, curr = df.iloc[i-1], df.iloc[i]
        # cross up
        if prev['SMA5'] <= prev['SMA20'] and curr['SMA5'] > curr['SMA20']:
            entry = curr['Close']; sl = curr['SMA20']
            target = entry + (entry - sl)*5
            fut = df.iloc[i+1:]
            win  = fut['High'].ge(target).any() and not fut['Low'].le(sl).any()
            trades.append((curr.name.date(), entry, sl, target, "WIN" if win else "LOSS"))
        # cross down
        if prev['SMA5'] >= prev['SMA20'] and curr['SMA5'] < curr['SMA20']:
            entry = curr['Close']; sl = curr['SMA20']
            target = entry - (sl - entry)*5
            fut = df.iloc[i+1:]
            win  = fut['Low'].le(target).any() and not fut['High'].ge(sl).any()
            trades.append((curr.name.date(), entry, sl, target, "WIN" if win else "LOSS"))
    bt = pd.DataFrame(trades, columns=['Date','Entry','SL','Target','Result'])
    return bt

# — Main —
symbol = st.text_input("Stock Symbol (e.g. RELIANCE.NS):", "RELIANCE.NS").strip().upper()
if not symbol: st.stop()

if mode == "Manual Analysis":
    manual_analyze(get_df(symbol, "3mo", "1d"), symbol)

elif mode == "Intraday Signals":
    signal, df_i = intraday_signals(get_df(symbol, "7d", "15m"), symbol)

elif mode == "Swing Signals":
    swing_signals(get_df(symbol, "1mo", "1d"), symbol)

elif mode == "5Y Backtest":
    st.subheader(f"📊 Backtesting {symbol} over 5 Years")
    bt = backtest(symbol)
    if bt.empty:
        st.info("No crossover trades found.")
    else:
        win_rate = (bt['Result']=="WIN").mean()*100
        st.metric("Total Trades", len(bt), delta=None)
        st.metric("Win Rate", f"{win_rate:.2f}%")
        st.dataframe(bt.tail(10))
