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
    try:
        # Check prerequisites first
        import os
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            return """
            <h1>❌ Configuration Error</h1>
            <p>GOOGLE_SHEET_ID not found in environment variables!</p>
            <p>Please add your Google Sheet ID to the Secrets tab in Replit.</p>
            <p><a href='/'>← Back to Dashboard</a></p>
            """
        
        if not os.path.exists("credintial.json"):
            return """
            <h1>❌ Credentials Error</h1>
            <p>Google credentials file not found!</p>
            <p><a href='/'>← Back to Dashboard</a></p>
            """
        
        # Start the bot
        threading.Thread(target=run_trading_bot).start()
        return """
        <h1>🚀 Crypto Trading Bot</h1>
        <p>✅ Bot has been started successfully via /run endpoint!</p>
        <p>🔄 The bot is now running 6 trading cycles in the background...</p>
        <p>⏱️ This will take about 1 minute to complete.</p>
        <p><strong>📋 What happens next:</strong></p>
        <ul>
            <li>🔍 Analyzing Reddit sentiment from 5 crypto subreddits</li>
            <li>📊 Making BTC price predictions using AI model</li>
            <li>💰 Executing buy/sell/hold decisions</li>
            <li>📝 Logging all trades to your Google Sheet</li>
            <li>📧 Sending email alerts for major trades</li>
        </ul>
        <p><a href='/status'>📊 Check Bot Status</a></p>
        <p><a href='/'>← Back to Dashboard</a></p>
        <p><strong>🔗 Your Google Sheet:</strong> <a href="https://docs.google.com/spreadsheets/d/1whYmmYjQTddVyLiHJxuQl_95rXQPC2yvlrq5yP32JFo/edit" target="_blank">View Trading Log</a></p>
        """
    except Exception as e:
        return f"""
        <h1>❌ Error Starting Bot</h1>
        <p>Error: {str(e)}</p>
        <p><a href='/'>← Back to Dashboard</a></p>
        """

@app.route("/status")
def status():
    reddit_id = "✅ Set" if os.getenv('REDDIT_CLIENT_ID') else "❌ Missing"
    model_status = "✅ Found" if os.path.exists("btc_lstm_model.h5") else "❌ Missing"
    scaler_status = "✅ Found" if os.path.exists("scaler.pkl") else "❌ Missing"
    creds_status = "✅ Found" if os.path.exists("credintial.json") else "❌ Missing"
    sheet_id = "✅ Set" if os.getenv('GOOGLE_SHEET_ID') else "❌ Missing"
    
    # Test Google Sheets connection
    sheets_connection = "❌ Not tested"
    if os.path.exists("credintial.json") and os.getenv('GOOGLE_SHEET_ID'):
        try:
            from trading_bot import setup_google_sheets
            sheet = setup_google_sheets("credintial.json", os.getenv('GOOGLE_SHEET_ID'), "trading_bot_log")
            sheets_connection = "✅ Connected"
        except Exception as e:
            sheets_connection = f"❌ Failed: {str(e)[:50]}..."
    
    return f"""
    <h2>🔧 Bot Status Dashboard</h2>
    <h3>📋 Configuration Status:</h3>
    <p>Reddit Client ID: {reddit_id}</p>
    <p>Google Sheet ID: {sheet_id}</p>
    <p>Google Credentials: {creds_status}</p>
    <p>Google Sheets Connection: {sheets_connection}</p>
    
    <h3>🤖 AI Model Status:</h3>
    <p>LSTM Model file: {model_status}</p>
    <p>Price Scaler file: {scaler_status}</p>
    
    <h3>🔗 Quick Links:</h3>
    <p><a href="/download-model">📥 Download Model Manually</a></p>
    <p><a href="https://docs.google.com/spreadsheets/d/1whYmmYjQTddVyLiHJxuQl_95rXQPC2yvlrq5yP32JFo/edit" target="_blank">📊 View Google Sheet</a></p>
    <p><a href="/run">🚀 Run Trading Bot</a></p>
    <p><a href="/">← Back to Dashboard</a></p>
    
    <h3>⚠️ Important Notes:</h3>
    <p>• Make sure you've shared your Google Sheet with: <code>trading-bot-logger@trading-bot-project-460614.iam.gserviceaccount.com</code></p>
    <p>• Give the service account "Editor" permissions</p>
    <p>• The bot takes about 60 seconds to complete all 6 trading cycles</p>
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
