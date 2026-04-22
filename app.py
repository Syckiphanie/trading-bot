from flask import Flask, render_template_string
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

pairs = [
    "EURUSD=X","GBPUSD=X","USDJPY=X","GBPJPY=X",
    "AUDUSD=X","USDCHF=X","USDCAD=X","NZDUSD=X"
]

def get_close(df):
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.astype(float)

def analyze(symbol):
    df = yf.download(symbol, period="1d", interval="1m")

    if df.empty or len(df) < 50:
        return "WAIT ⏳"

    close = get_close(df)

    rsi = RSIIndicator(close).rsi().iloc[-1]
    macd = MACD(close)
    macd_val = macd.macd().iloc[-1]
    macd_sig = macd.macd_signal().iloc[-1]

    ema50 = EMAIndicator(close, window=50).ema_indicator().iloc[-1]
    ema200 = EMAIndicator(close, window=200).ema_indicator().iloc[-1]

    last_close = close.iloc[-1]
    prev_close = close.iloc[-2]

    if ema50 > ema200 and macd_val > macd_sig and last_close > prev_close and rsi < 60:
        return "BUY 🟢"

    elif ema50 < ema200 and macd_val < macd_sig and last_close < prev_close and rsi > 40:
        return "SELL 🔴"

    return "WAIT ⏳"

def get_entry_time():
    now = datetime.now()
    entry = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    return entry.strftime("%H:%M")

@app.route("/")
def home():
    results = []

    for pair in pairs:
        signal = analyze(pair)
        entry = get_entry_time()

        results.append({
            "pair": pair,
            "signal": signal,
            "entry": entry
        })

    html = """
    <html>
    <head>
    <title>AI Trading Bot</title>

    <!-- 🔄 AUTO REFRESH -->
    <meta http-equiv="refresh" content="10">

    <style>
    body {
        background:#0f172a;
        color:white;
        font-family:Arial;
        text-align:center;
    }

    .title {
        font-size:28px;
        margin-top:20px;
    }

    .card {
        background:#1e293b;
        padding:20px;
        margin:20px auto;
        border-radius:15px;
        width:300px;
        box-shadow:0 0 15px rgba(0,0,0,0.5);
    }

    .buy {
        color:#22c55e;
        font-size:22px;
        font-weight:bold;
    }

    .sell {
        color:#ef4444;
        font-size:22px;
        font-weight:bold;
    }

    .wait {
        color:#facc15;
        font-size:18px;
    }

    </style>
    </head>

    <body>

    <h1 class="title">🤖 AI LIVE SIGNAL</h1>

    {% for r in results %}
    <div class="card">
        <h2>{{r.pair}}</h2>

        {% if "BUY" in r.signal %}
            <p class="buy">{{r.signal}}</p>
        {% elif "SELL" in r.signal %}
            <p class="sell">{{r.signal}}</p>
        {% else %}
            <p class="wait">{{r.signal}}</p>
        {% endif %}

        <p>⏱️ Antre: {{r.entry}}</p>
    </div>
    {% endfor %}

    </body>
    <audio id="alertSound" src="https://www.soundjay.com/buttons/sounds/beep-07.mp3"></audio>

<script>
let lastSignal = "";

function checkSignal(){
    fetch("/")
    .then(res => res.text())
    .then(data => {
        if(lastSignal !== "" && data !== lastSignal){
            document.getElementById("alertSound").play();
        }
        lastSignal = data;
    });
}

setInterval(checkSignal, 10000);
</script>
    </html>
    <div class="tradingview-widget-container">
  <div id="tradingview_chart"></div>
</div>

<script src="https://s3.tradingview.com/tv.js"></script>

<script>
new TradingView.widget({
  "width": "100%",
  "height": 400,
  "symbol": "FX:EURUSD",
  "interval": "1",
  "timezone": "Etc/UTC",
  "theme": "dark",
  "style": "1",
  "locale": "en",
  "container_id": "tradingview_chart"
});
</script>
    """

    return render_template_string(html, results=results)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
