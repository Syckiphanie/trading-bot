from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from datetime import datetime, timedelta
import os

app = Flask(__name__)

pairs = [
    "EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X",
    "USDCHF=X","NZDUSD=X","EURGBP=X","EURJPY=X","GBPJPY=X"
]

def get_signal(symbol):
    df = yf.download(symbol, period="1d", interval="1m")

    if df.empty:
        return None, None

    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    rsi = RSIIndicator(close).rsi()
    macd = MACD(close)
    ema = EMAIndicator(close, window=50).ema_indicator()

    last_rsi = rsi.iloc[-1]
    last_macd = macd.macd_diff().iloc[-1]
    last_price = close.iloc[-1]
    last_ema = ema.iloc[-1]

    if last_rsi < 30 and last_macd > 0 and last_price > last_ema:
        return "BUY", symbol.replace("=X","")
    elif last_rsi > 70 and last_macd < 0 and last_price < last_ema:
        return "SELL", symbol.replace("=X","")
    else:
        return None, None

@app.route("/")
def index():
    results = []

    now = datetime.now()
    entry_time = (now + timedelta(minutes=1)).strftime("%H:%M")

    for pair in pairs:
        signal, clean_pair = get_signal(pair)
        if signal:
            results.append((clean_pair, signal))

    html = """
    <html>
    <head>
    <title>🔥 PRO SIGNAL BOT</title>

    <script src="https://s3.tradingview.com/tv.js"></script>

    <style>
    body { background:#0f172a; color:white; font-family:Arial; text-align:center; }
    .card {
        border:2px solid #38bdf8;
        margin:10px;
        padding:15px;
        border-radius:10px;
    }
    .buy { color:lime; font-size:22px; }
    .sell { color:red; font-size:22px; }
    </style>

    </head>

    <body>

    <h1>🤖 PRO SIGNAL BOT</h1>
    <h3>⏱️ Antre: {{time}}</h3>

    {% for pair, signal in results %}
    <div class="card">
        <h2>{{pair}}</h2>

        {% if signal == "BUY" %}
            <p class="buy">🟢 BUY</p>
        {% else %}
            <p class="sell">🔴 SELL</p>
        {% endif %}

        <!-- 📊 GRAFIK -->
        <div id="chart_{{pair}}" style="height:300px;"></div>

        <script>
        new TradingView.widget({
            "container_id": "chart_{{pair}}",
            "width": "100%",
            "height": 300,
            "symbol": "FX:{{pair}}",
            "interval": "1",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "toolbar_bg": "#0f172a",
            "enable_publishing": false,
            "hide_top_toolbar": true,
            "hide_legend": true
        });
        </script>

    </div>
    {% endfor %}

    <!-- 🔔 SOUND -->
    <audio id="sound" src="https://www.soundjay.com/buttons/sounds/beep-07.mp3"></audio>

    <script>
    let last = "";

    setInterval(() => {
        fetch("/")
        .then(r => r.text())
        .then(data => {
            if(last && data !== last){
                document.getElementById("sound").play();
            }
            last = data;
        });
    }, 10000);
    </script>

    </body>
    </html>
    """

    return render_template_string(html, results=results, time=entry_time)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
