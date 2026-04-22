from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from datetime import datetime, timedelta
import os

app = Flask(__name__)

pairs = ["EURUSD=X","GBPUSD=X","USDJPY=X","GBPJPY=X"]

def get_signal(symbol):
    df = yf.download(symbol, period="1d", interval="1m")

    if df.empty:
        return None

    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    rsi = RSIIndicator(close).rsi()
    macd = MACD(close)
    ema = EMAIndicator(close, window=50).ema_indicator()

    if rsi.iloc[-1] < 40 and macd.macd_diff().iloc[-1] > 0:
        return "BUY"
    elif rsi.iloc[-1] > 60 and macd.macd_diff().iloc[-1] < 0:
        return "SELL"
    else:
        return None

@app.route("/")
def index():
    results = []
    now = datetime.now()
    entry_time = (now + timedelta(minutes=1)).strftime("%H:%M")

    for pair in pairs:
        signal = get_signal(pair)
        if signal:
            results.append((pair.replace("=X",""), signal))

    html = """
    <html>
    <head>
    <title>🤖 PRO BOT</title>

    <style>
    body {background:#0f172a;color:white;font-family:Arial;text-align:center;}
    .card {
        border:2px solid #38bdf8;
        margin:10px;
        padding:15px;
        border-radius:10px;
    }
    .buy {color:lime;font-size:22px;}
    .sell {color:red;font-size:22px;}
    </style>

    </head>

    <body>

    <h1>🤖 PRO SIGNAL BOT</h1>
    <h3>⏱️ Antre: {{time}}</h3>

    <!-- 📊 GRAF KI MACHE 100% -->
    <div style="margin:20px;">
        <iframe 
        src="https://s.tradingview.com/widgetembed/?symbol=FX:EURUSD&interval=1&theme=dark&style=1"
        width="100%" height="400" frameborder="0"></iframe>
    </div>

    {% for pair, signal in results %}
    <div class="card">
        <h2>{{pair}}</h2>

        {% if signal == "BUY" %}
            <p class="buy">🟢 BUY</p>
        {% else %}
            <p class="sell">🔴 SELL</p>
        {% endif %}
    </div>
    {% endfor %}

    </body>
    </html>
    """

    return render_template_string(html, results=results, time=entry_time)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
