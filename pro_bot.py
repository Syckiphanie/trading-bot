import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
import requests
import time
import pandas as pd
from datetime import datetime, timedelta

TOKEN = "8646548467:AAEJTYZNBlBkaEERmYhyOiHV1kAAEbpkeDY"
CHAT_ID = "802735782"

pairs = [
    "EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCHF=X","USDCAD=X","NZDUSD=X",
    "EURGBP=X","EURJPY=X","EURCHF=X","EURAUD=X","EURCAD=X","EURNZD=X",
    "GBPJPY=X","GBPCHF=X","GBPAUD=X","GBPCAD=X","GBPNZD=X",
    "AUDJPY=X","AUDCHF=X","AUDCAD=X","AUDNZD=X",
    "CADJPY=X","CADCHF=X","CHFJPY=X",
    "NZDJPY=X","NZDCHF=X","NZDCAD=X",
    "USDHKD=X","USDSGD=X","USDZAR=X","USDTRY=X","USDMXN=X",
    "EURZAR=X","EURTRY=X","GBPZAR=X","GBPSGD=X",
    "AUDSGD=X","AUDHKD=X"
]

last_signals = {}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": msg})

def get_close(df):
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.astype(float)

def get_entry_time():
    now = datetime.now()
    next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    expiry = next_minute + timedelta(minutes=1)

    entry_time = next_minute.strftime("%H:%M")
    expiry_time = expiry.strftime("%H:%M")

    return entry_time, expiry_time

def format_signal(symbol, signal):
    entry_time, expiry_time = get_entry_time()

    color_signal = "🟢 BUY 📈" if "BUY" in signal else "🔴 SELL 📉"

    msg = f"""
╔══════════════════════╗
        🤖 AI SIGNAL
╠══════════════════════╣
📊 PAIR: {symbol}
📍 SIGNAL: {color_signal}
⏱️ ANTRE: {entry_time}
⏳ EXPIRY: {expiry_time}
🧠 MODE: SMART AI PRO
╚══════════════════════╝
"""
    return msg

def analyze(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m")

        if df.empty or len(df) < 50:
            return None

        close = get_close(df)

        rsi = RSIIndicator(close).rsi().iloc[-1]
        macd = MACD(close)
        macd_val = macd.macd().iloc[-1]
        macd_sig = macd.macd_signal().iloc[-1]

        ema50 = EMAIndicator(close, window=50).ema_indicator().iloc[-1]
        ema200 = EMAIndicator(close, window=200).ema_indicator().iloc[-1]

        last_close = close.iloc[-1]
        prev_close = close.iloc[-2]

        # 🧠 AI SMART LOGIC (pi entelijan)
        if (ema50 > ema200 and 
            macd_val > macd_sig and 
            last_close > prev_close and 
            45 < rsi < 65):
            return "BUY"

        elif (ema50 < ema200 and 
              macd_val < macd_sig and 
              last_close < prev_close and 
              35 < rsi < 55):
            return "SELL"

        return None

    except Exception as e:
        print(f"Error {symbol}: {e}")
        return None

send_telegram("🚀 AI SMART BOT AKTIF")

while True:
    for pair in pairs:
        time.sleep(1)

        signal = analyze(pair)

        if signal and last_signals.get(pair) != signal:
            last_signals[pair] = signal

            msg = format_signal(pair, signal)
            print(msg)
            send_telegram(msg)

    print("Scan fini... ⏳")
    time.sleep(60)