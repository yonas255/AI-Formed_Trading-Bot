from flask import Flask, render_template_string, send_file
import threading
import os
from trading_bot import run_trading_bot

app = Flask(__name__)

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Trading Bot Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f7fa;
            color: #333;
            padding: 40px;
        }
        h1 {
            color: #1a73e8;
        }
        .card {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        a.button {
            display: inline-block;
            background: #1a73e8;
            color: white;
            padding: 10px 20px;
            margin: 10px 0;
            border-radius: 8px;
            text-decoration: none;
        }
        a.button:hover {
            background: #0f59c2;
        }
        footer {
            margin-top: 40px;
            font-size: 0.9em;
            color: #777;
        }
        img {
            max-width: 100%;
            margin-top: 20px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <h1>🚀 Crypto Trading Bot Dashboard</h1>
    <div class="card">
        <p>Welcome to the AI-Powered Crypto Trading Bot.</p>
        <a class="button" href="/start-bot">▶️ Start Trading Bot</a><br>
        <a class="button" href="/status">📊 View Bot Status</a><br>
        <a class="button" href="/download-model">📥 Download Model</a><br>
        <a class="button" href="/download-log">📝 Download Log</a><br>
        <a class="button" href="/view-results">📈 View Run Chart</a><br>
        <a class="button" href="/stop">🛑 Stop Bot (not yet implemented)</a>
    </div>
    <footer>
        Built with ❤️ by Your AI Bot | Check your Google Sheet for trading logs
    </footer>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route("/start-bot")
def start_bot():
    threading.Thread(target=run_trading_bot).start()
    return """
    <h2>🚀 Crypto Trading Bot</h2>
    <p>✅ Bot has been started successfully via /start-bot endpoint!</p>
    <p>🔄 It will analyze sentiment, make predictions, trade, and log results.</p>
    <a href="/">← Back to Dashboard</a>
    """

@app.route("/status")
def status():
    from os import path, getenv
    return f"""
    <h2>📊 Bot Status</h2>
    <ul>
        <li>Reddit Client ID: {'✅ Set' if getenv('REDDIT_CLIENT_ID') else '❌ Missing'}</li>
        <li>Model file: {'✅ Found' if path.exists('btc_lstm_model.h5') else '❌ Missing'}</li>
        <li>Scaler file: {'✅ Found' if path.exists('scaler.pkl') else '❌ Missing'}</li>
        <li>Credentials: {'✅ Found' if path.exists('credintial.json') else '❌ Missing'}</li>
    </ul>
    <a href="/">← Back to Dashboard</a>
    """

@app.route("/download-model")
def download_model():
    from trading_bot import download_model_from_github
    success = download_model_from_github()
    return "✅ Model downloaded." if success else "❌ Failed to download model."

@app.route("/download-log")
def download_log():
    log_path = "sentiment_trade_log.txt"
    if os.path.exists(log_path):
        return send_file(log_path, as_attachment=True)
    return "❌ No log file found."

@app.route("/view-results")
def view_results():
    chart_path = "run_results_chart.png"
    if os.path.exists(chart_path):
        return f"""
        <h2>📈 Bot Run Chart</h2>
        <img src='/static/{chart_path}' alt='Run Chart'>
        <p><a href="/">← Back to Dashboard</a></p>
        """
    return "❌ Chart not found. Run the bot first."

@app.route("/stop")
def stop():
    return "🛑 Stop functionality is not implemented yet."

@app.route("/run")
def auto_trigger():
    threading.Thread(target=run_trading_bot).start()
    return "✅ Bot has been started via /run"

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
