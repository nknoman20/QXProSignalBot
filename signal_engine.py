import requests
import os
import pandas as pd
import ta

API_KEY = os.getenv("TWELVEDATA_API_KEY")

PAIRS = {
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "USD/JPY": "USD/JPY",
    "AUD/USD": "AUD/USD",
    "USD/CAD": "USD/CAD"
}

def fetch_data(symbol):
    print(f"📥 Fetching data for: {symbol}")
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=50&apikey={API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if "values" not in data:
            print(f"❌ No 'values' in response for {symbol}: {data}")
            return None
        df = pd.DataFrame(data["values"])
        df = df.rename(columns={"datetime": "date", "close": "close"})
        df["close"] = pd.to_numeric(df["close"])
        df = df.sort_values("date")
        print(f"✅ Data fetched for {symbol}, rows: {len(df)}")
        return df
    except Exception as e:
        print(f"🔥 Exception in fetch_data({symbol}): {e}")
        return None

def analyze(df):
    try:
        df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
        df["ema_9"] = ta.trend.EMAIndicator(df["close"], window=9).ema_indicator()
        df["ema_21"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        print(f"📈 RSI: {latest['rsi']:.2f}, EMA9: {latest['ema_9']:.5f}, EMA21: {latest['ema_21']:.5f}")

        signal = None
        reason = ""

        if latest["rsi"] < 30 and latest["ema_9"] > latest["ema_21"]:
            signal = "BUY"
            reason = "RSI Oversold & EMA Crossover (Up)"
        elif latest["rsi"] > 70 and latest["ema_9"] < latest["ema_21"]:
            signal = "SELL"
            reason = "RSI Overbought & EMA Crossover (Down)"

        return signal, reason
    except Exception as e:
        print(f"🔥 Exception in analyze(): {e}")
        return None, None

def generate_signal():
    print("🔁 Generating signal...")
    for name, symbol in PAIRS.items():
        df = fetch_data(symbol)
        if df is not None and len(df) > 21:
            print(f"🔍 Analyzing {name}...")
            signal, reason = analyze(df)
            if signal:
                print(f"✅ Signal found: {name} - {signal} ({reason})")
                return name, signal, reason
            else:
                print(f"⚠️ No valid signal for {name}")
        else:
            print(f"⚠️ Skipped {name} due to insufficient data")
