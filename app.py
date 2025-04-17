import streamlit as st
import yfinance as yf
import pandas as pd

# Config
st.set_page_config(page_title="SweetTrade Pro v2.0", layout="wide")
st.title("💘 SweetTrade Pro v2.0 – SMC+ICT | Manual | Intraday | Swing | Backtest")

mode = st.sidebar.radio("🧠 Select Mode:", [
    "Manual Analysis", "Intraday Signals", "Swing Signals", "5Y Backtest"
])

# Download helper
def get_df(symbol, period, interval):
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    df.columns = df.columns.get_level_values(0) if isinstance(df.columns, pd.MultiIndex) else df.columns
    return df.dropna()

# Signal Evaluator
def evaluate_signal(df, price, sl, target):
    if price >= target: return "🟢 Exit – Target Hit"
    if price <= sl: return "🔴 Exit – Stop-Loss Hit"
    if price >= price * 1.02: return "🟡 Trail SL"
    if price <= price * 0.98: return "🟡 Trail SL"
    return "⚪ Hold"

# UI block for signals
def show_signal_block(symbol, signal, price, sl, target, guidance, df_slice, chart_cols):
    st.success(f"{symbol} → {signal}")
    st.write(f"• Entry: `{price:.2f}`")
    if sl: st.write(f"• Stop-Loss: `{sl:.2f}`")
    if target: st.write(f"• Target: `{target:.2f}`")
    st.info(f"🔍 Guidance: {guidance}")
    st.line_chart(df_slice[chart_cols])

# Manual Mode
def manual_analysis(df, symbol):
    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['EMA10'] = df['Close'].ewm(span=10, adjust=False).mean()
    df.dropna(inplace=True)

    latest = df.iloc[-1]
    price, sma20, sma50 = latest['Close'], latest['SMA20'], latest['SMA50']
    bullish = price > sma50 and price > sma20
    bearish = price < sma50 and price < sma20

    if bullish:
        signal, sl = "📈 BUY SETUP", sma50
        target = price + (price - sl) * 5
    elif bearish:
        signal, sl = "📉 SELL SETUP", sma50
        target = price - (sl - price) * 5
    else:
        signal = "⚖️ NO CLEAR SETUP"
        sl = target = None

    guidance = evaluate_signal(df['Close'].iloc[-1], sl, target) if sl else "⚪ No Setup"
    st.subheader(f"📊 Data for {symbol}")
    st.dataframe(df.tail(5)[['Close','SMA20','SMA50','EMA10']])
    st.subheader("🎯 Signal")
    show_signal_block(symbol, signal, price, sl, target, guidance, df, ['Close','SMA20','SMA50'])

# Intraday Mode
def intraday_signals(df, symbol):
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df.dropna(inplace=True)
    price, ema9 = df['Close'].iloc[-1], df['EMA9'].iloc[-1]

    if price > ema9:
        signal = "📈 BUY"
        sl = ema9
        target = price + (price - sl) * 5
    elif price < ema9:
        signal = "📉 SELL"
        sl = ema9
        target = price - (sl - price) * 5
    else:
        signal, sl, target = "⚖️ HOLD", None, None

    guidance = evaluate_signal(price, sl, target) if sl else "⚪ Hold"
    show_signal_block(symbol, signal, price, sl, target, guidance, df, ['Close','EMA9'])

# Swing Mode
def swing_signals(df, symbol):
    df['SMA5'] = df['Close'].rolling(5).mean()
    df['SMA20'] = df['Close'].rolling(20).mean()
    df.dropna(inplace=True)
    price, sma5, sma20 = df['Close'].iloc[-1], df['SMA5'].iloc[-1], df['SMA20'].iloc[-1]

    if sma5 > sma20:
        signal = "📈 BUY"
        sl = sma20
        target = price + (price - sl) * 5
    elif sma5 < sma20:
        signal = "📉 SELL"
        sl = sma20
        target = price - (sl - price) * 5
    else:
        signal, sl, target = "⚖️ HOLD", None, None

    guidance = evaluate_signal(price, sl, target) if sl else "⚪ Hold"
    show_signal_block(symbol, signal, price, sl, target, guidance, df, ['Close','SMA5','SMA20'])

# Backtesting
def backtest(symbol):
    df = get_df(symbol, "5y", "1d")
    df['SMA5'] = df['Close'].rolling(5).mean()
    df['SMA20'] = df['Close'].rolling(20).mean()
    df.dropna(inplace=True)
    trades = []

    for i in range(1, len(df)-1):
        prev, curr = df.iloc[i-1], df.iloc[i]
        next_rows = df.iloc[i+1:]
        if prev['SMA5'] <= prev['SMA20'] and curr['SMA5'] > curr['SMA20']:
            entry, sl = curr['Close'], curr['SMA20']
            target = entry + (entry - sl)*5
            win = next_rows['High'].ge(target).any() and not next_rows['Low'].le(sl).any()
            trades.append((curr.name.date(), entry, sl, target, "WIN" if win else "LOSS"))
        elif prev['SMA5'] >= prev['SMA20'] and curr['SMA5'] < curr['SMA20']:
            entry, sl = curr['Close'], curr['SMA20']
            target = entry - (sl - entry)*5
            win = next_rows['Low'].le(target).any() and not next_rows['High'].ge(sl).any()
            trades.append((curr.name.date(), entry, sl, target, "WIN" if win else "LOSS"))

    return pd.DataFrame(trades, columns=['Date','Entry','SL','Target','Result'])

# Input
symbol = st.text_input("🧾 Enter Stock Symbol:", "RELIANCE.NS").upper().strip()
if not symbol: st.stop()

if mode == "Manual Analysis":
    manual_analysis(get_df(symbol, "3mo", "1d"), symbol)

elif mode == "Intraday Signals":
    intraday_signals(get_df(symbol, "7d", "15m"), symbol)

elif mode == "Swing Signals":
    swing_signals(get_df(symbol, "1mo", "1d"), symbol)

elif mode == "5Y Backtest":
    st.subheader(f"📊 5Y Backtest – {symbol}")
    bt = backtest(symbol)
    if bt.empty:
        st.info("⚠️ No crossover trades found.")
    else:
        winrate = (bt['Result']=="WIN").mean() * 100
        st.metric("📈 Total Trades", len(bt))
        st.metric("🏆 Win Rate", f"{winrate:.2f}%")
        st.dataframe(bt.tail(10))
