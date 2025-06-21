
from flask import Flask, render_template_string, send_file, jsonify
import threading
import os
from trading_bot import run_trading_bot
from datetime import datetime

app = Flask(__name__)

# Enhanced Dashboard Template with better UI
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Crypto Trading Bot Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 15px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 20px 0;
        }
        
        .header h1 {
            font-size: clamp(2rem, 5vw, 3rem);
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-weight: 700;
        }
        
        .header p {
            font-size: clamp(1rem, 3vw, 1.2rem);
            opacity: 0.9;
            margin: 0 10px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        .card h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: clamp(1.1rem, 2.5vw, 1.4rem);
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
        }
        
        .button {
            display: inline-block;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 14px 20px;
            margin: 6px 3px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.2);
            border: none;
            cursor: pointer;
            font-size: clamp(0.85rem, 2vw, 0.95rem);
            text-align: center;
            min-width: 120px;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
        }
        
        .button:hover, .button:focus {
            transform: translateY(-2px);
            box-shadow: 0 5px 18px rgba(0, 0, 0, 0.3);
            outline: none;
        }
        
        .button:active {
            transform: translateY(0px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        
        .button.danger {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        }
        
        .button.success {
            background: linear-gradient(45deg, #4ecdc4, #44a08d);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            flex-shrink: 0;
        }
        
        .status-online {
            background: #2ecc71;
            animation: pulse 2s infinite;
        }
        
        .status-offline {
            background: #e74c3c;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }
        
        .stat-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: clamp(1.1rem, 3vw, 1.3rem);
            font-weight: bold;
            color: #333;
        }
        
        .stat-label {
            font-size: clamp(0.8rem, 2vw, 0.9rem);
            color: #666;
            margin-top: 3px;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
            font-size: clamp(0.8rem, 2vw, 0.9rem);
            padding: 15px;
        }
        
        .alert {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid #ffc107;
            color: #856404;
            padding: 12px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: clamp(0.85rem, 2vw, 0.95rem);
        }
        
        .log-preview {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: clamp(0.7rem, 1.8vw, 0.85rem);
            max-height: 150px;
            overflow-y: auto;
            margin: 10px 0;
            line-height: 1.4;
        }
        
        /* Mobile-specific optimizations */
        @media screen and (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .header {
                margin-bottom: 20px;
                padding: 10px 0;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr;
                gap: 12px;
                margin-bottom: 20px;
            }
            
            .card {
                padding: 15px;
                border-radius: 12px;
            }
            
            .button {
                padding: 12px 16px;
                margin: 5px 2px;
                width: calc(50% - 6px);
                display: inline-block;
                text-align: center;
                font-size: 0.9rem;
            }
            
            .footer {
                margin-top: 20px;
                padding: 10px;
            }
            
            .alert {
                padding: 10px;
                margin: 10px 0;
            }
        }
        
        @media screen and (max-width: 480px) {
            .button {
                width: 100%;
                margin: 4px 0;
                padding: 14px 12px;
            }
            
            .card h3 {
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }
            
            .stat-item {
                padding: 10px;
            }
        }
        
        /* Touch-friendly improvements */
        @media (hover: none) and (pointer: coarse) {
            .button:hover {
                transform: none;
            }
            
            .card:hover {
                transform: none;
            }
            
            .button {
                padding: 16px 20px;
            }
        }
        
        /* Landscape phone optimization */
        @media screen and (max-height: 500px) and (orientation: landscape) {
            .header h1 {
                font-size: 2rem;
                margin-bottom: 5px;
            }
            
            .header p {
                font-size: 1rem;
            }
            
            .header {
                margin-bottom: 15px;
                padding: 5px 0;
            }
            
            .card {
                padding: 12px;
            }
        }
        
        /* High DPI displays */
        @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
            .button {
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Crypto Trading Bot</h1>
            <p>AI-Powered Bitcoin Trading with Sentiment Analysis</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>🎮 Bot Controls</h3>
                <div class="alert">
                    <strong>Status:</strong> 
                    <span class="status-indicator status-{{ 'online' if bot_running else 'offline' }}"></span>
                    {{ 'Running' if bot_running else 'Stopped' }}
                </div>
                <a class="button success" href="{{ url_for('start_bot') }}">▶️ Start Trading Bot</a>
                <a class="button danger" href="{{ url_for('stop_bot') }}">🛑 Stop Bot</a>
                <a class="button" href="{{ url_for('run_once') }}">⚡ Run Once</a>
            </div>
            
            <div class="card">
                <h3>📊 Monitoring</h3>
                <a class="button" href="{{ url_for('status') }}">📈 Bot Status</a>
                <a class="button" href="{{ url_for('view_results') }}">📊 View Charts</a>
                <a class="button" href="{{ url_for('download_log') }}">📝 Download Logs</a>
                <a class="button" href="https://docs.google.com/spreadsheets/d/1whYmmYjQTddVyLiHJxuQl_95rXQPC2yvlrq5yP32JFo/edit" target="_blank">📋 Google Sheet</a>
            </div>
            
            <div class="card">
                <h3>🔧 Configuration</h3>
                <a class="button" href="{{ url_for('download_model') }}">📥 Download Model</a>
                <a class="button" href="{{ url_for('test_connections') }}">🔍 Test APIs</a>
                <a class="button" href="{{ url_for('health') }}">💚 Health Check</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Built with ❤️ using Flask & AI | Last Updated: {{ current_time }}</p>
        </div>
    </div>
</body>
</html>
"""

# Global bot state
bot_running = False
bot_thread = None

@app.route("/")
def home():
    return render_template_string(DASHBOARD_TEMPLATE, 
                                bot_running=bot_running, 
                                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route("/start-bot")
def start_bot():
    global bot_running, bot_thread
    if not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=run_trading_bot_wrapper)
        bot_thread.start()
        message = "✅ Bot started successfully!"
        status_class = "success"
    else:
        message = "⚠️ Bot is already running!"
        status_class = "warning"
    
    return f"""
    <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
            <h2 style="color: #333;">🚀 Trading Bot Control</h2>
            <div style="background: {'#d4edda' if status_class == 'success' else '#fff3cd'}; padding: 20px; border-radius: 10px; margin: 20px 0;">
                {message}
            </div>
            <p style="color: #666; margin: 20px 0;">The bot will analyze sentiment, make AI predictions, and execute trades.</p>
            <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">← Back to Dashboard</a>
            <a href="/status" style="background: #764ba2; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">📊 View Status</a>
        </div>
    </div>
    """

@app.route("/stop-bot")
def stop_bot():
    global bot_running
    bot_running = False
    return """
    <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
            <h2>🛑 Bot Stopped</h2>
            <p>The trading bot has been stopped successfully.</p>
            <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
        </div>
    </div>
    """

@app.route("/run-once")
def run_once():
    threading.Thread(target=run_trading_bot).start()
    return """
    <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
            <h2>⚡ Single Run Executed</h2>
            <p>✅ Bot executed one trading cycle successfully!</p>
            <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
        </div>
    </div>
    """

@app.route("/status")
def status():
    from os import path, getenv
    
    checks = {
        "Reddit API": "✅ Connected" if getenv('REDDIT_CLIENT_ID') else "❌ Missing Client ID",
        "AI Model": "✅ Ready" if path.exists('btc_lstm_model.h5') else "❌ Missing Model",
        "Price Scaler": "✅ Ready" if path.exists('scaler.pkl') else "❌ Missing Scaler",
        "Google Credentials": "✅ Found" if path.exists('credintial.json') else "❌ Missing Credentials",
        "Google Sheet ID": "✅ Configured" if getenv('GOOGLE_SHEET_ID') else "❌ Not Set",
        "Log File": "✅ Active" if path.exists('sentiment_trade_log.txt') else "📝 Not Started"
    }
    
    return f"""
    <div style="padding: 20px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 800px; margin: 0 auto;">
            <h2 style="text-align: center; color: #333;">📊 Bot System Status</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">
                {''.join([f'<div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid {"#28a745" if "✅" in status else "#dc3545"};"><strong>{component}:</strong><br>{status}</div>' for component, status in checks.items()])}
            </div>
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">← Dashboard</a>
                <a href="/test-connections" style="background: #28a745; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">🔍 Test Connections</a>
            </div>
        </div>
    </div>
    """

@app.route("/test-connections")
def test_connections():
    results = []
    try:
        import praw
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )
        reddit.user.me()
        results.append("✅ Reddit API: Connected")
    except:
        results.append("❌ Reddit API: Failed")
    
    try:
        from trading_bot import setup_google_sheets
        sheet = setup_google_sheets("credintial.json", os.getenv('GOOGLE_SHEET_ID'), "trading_bot_log")
        results.append("✅ Google Sheets: Connected")
    except:
        results.append("❌ Google Sheets: Failed")
    
    return f"""
    <div style="padding: 20px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
            <h2 style="text-align: center;">🔍 Connection Test Results</h2>
            <div style="margin: 30px 0;">
                {'<br>'.join([f'<div style="padding: 10px; margin: 10px 0; background: {"#d4edda" if "✅" in result else "#f8d7da"}; border-radius: 5px;">{result}</div>' for result in results])}
            </div>
            <div style="text-align: center;">
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
            </div>
        </div>
    </div>
    """

@app.route("/download-model")
def download_model():
    from trading_bot import download_model_from_github
    success = download_model_from_github()
    return f"{'✅ Model downloaded successfully!' if success else '❌ Failed to download model.'} <a href='/'>← Back</a>"

@app.route("/download-log")
def download_log():
    log_path = "sentiment_trade_log.txt"
    if os.path.exists(log_path):
        return send_file(log_path, as_attachment=True)
    return "❌ No log file found. <a href='/'>← Back</a>"

@app.route("/view-results")
def view_results():
    chart_path = "run_results_chart.png"
    if os.path.exists(chart_path):
        return send_file(chart_path, mimetype='image/png')
    return "❌ Chart not found. Run the bot first. <a href='/'>← Back</a>"

@app.route("/run")
def auto_trigger():
    threading.Thread(target=run_trading_bot).start()
    return "✅ Bot started via /run endpoint"

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "bot_running": bot_running,
        "timestamp": datetime.now().isoformat()
    }), 200

def run_trading_bot_wrapper():
    """Wrapper to handle bot state"""
    global bot_running
    try:
        run_trading_bot()
    finally:
        bot_running = False

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
