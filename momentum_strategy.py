import yfinance as yf
import pandas as pd
import time

def get_data(symbol):
    df = yf.download(symbol, period="7d", interval="1h")
    df['RSI'] = calculate_rsi(df['Close'], 14)
    return df

def calculate_rsi(data, window):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def evaluate_signal(df):
    latest_rsi = df['RSI'].iloc[-1]
    if latest_rsi > 70:
        return "📉 SELL"
    elif latest_rsi < 30:
        return "📈 BUY"
    return "⚖️ HOLD"

def trade_logic(symbol):
    df = get_data(symbol)
    signal = evaluate_signal(df)
    return f"Signal for {symbol}: {signal}"

# Run every hour
def get_signal():
    return trade_logic("RELIANCE.NS")
