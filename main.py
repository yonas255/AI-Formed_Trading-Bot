import os
import threading
from flask import Flask
from dotenv import load_dotenv
from trading_bot import run_trading_bot

app = Flask(__name__)
load_dotenv()

@app.route("/")
def home():
    return """
    <h1>🚀 Crypto Trading Bot Dashboard</h1>
    <p><a href='/status'>📊 Check Bot Status</a></p>
    <p><a href='/start-bot'>🚀 Start Trading Bot</a></p>
    <p><a href='/download-model'>📥 Download Model</a></p>
    """

@app.route("/start-bot")
def trigger_bot():
    threading.Thread(target=run_trading_bot).start()
    return """
    <h1>🚀 Crypto Trading Bot</h1>
    <p>✅ Bot has been started successfully!</p>
    <p><a href='/'>← Back to Dashboard</a></p>
    """

@app.route("/run")
def auto_trigger():
    threading.Thread(target=run_trading_bot).start()
    return "✅ Bot triggered via /run", 200

@app.route("/status")
def status():
    reddit_id = "✅ Set" if os.getenv('REDDIT_CLIENT_ID') else "❌ Missing"
    model_status = "✅ Found" if os.path.exists("btc_lstm_model.h5") else "❌ Missing"
    scaler_status = "✅ Found" if os.path.exists("scaler.pkl") else "❌ Missing"
    creds_status = "✅ Found" if os.path.exists("credintial.json") else "❌ Missing"
    return f"""
    <h2>Bot Status</h2>
    <p>Reddit Client ID: {reddit_id}</p>
    <p>Model file: {model_status}</p>
    <p>Scaler file: {scaler_status}</p>
    <p>Credentials: {creds_status}</p>
    <p><a href="/download-model">Download Model Manually</a></p>
    """

@app.route("/download-model")
def manual_download():
    from trading_bot import download_model_from_github
    success = download_model_from_github()
    if success:
        return "✅ Model downloaded successfully! <a href='/status'>Check Status</a>"
    else:
        return "❌ Failed to download model. Please check the GitHub URL. <a href='/status'>Check Status</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
