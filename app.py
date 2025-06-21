
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
last_run_results = {}

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
    # Store results in a global variable to display them
    global last_run_results
    last_run_results = {}
    
    def run_with_results():
        global last_run_results
        try:
            last_run_results = run_trading_bot_with_results()
        except Exception as e:
            last_run_results = {"error": str(e)}
    
    threading.Thread(target=run_with_results).start()
    
    # Wait longer for the results (sentiment analysis takes time)
    import time
    max_wait = 30  # Wait up to 30 seconds
    wait_interval = 1
    waited = 0
    
    while waited < max_wait and not last_run_results:
        time.sleep(wait_interval)
        waited += wait_interval
    
    if "error" in last_run_results:
        return f"""
        <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
            <div style="background: white; padding: 40px; border-radius: 20px; max-width: 800px; margin: 0 auto;">
                <h2>❌ Run Failed</h2>
                <p style="color: red;">Error: {last_run_results['error']}</p>
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
            </div>
        </div>
        """
    
    results = last_run_results
    if not results:
        return """
        <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
            <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
                <h2>⚡ Bot is Running...</h2>
                <p>✅ Bot execution started! Results will be ready in a moment.</p>
                <a href="/results" style="background: #28a745; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">📊 View Results</a>
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
            </div>
        </div>
        """
    
    return f"""
    <div style="padding: 20px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 40px; border-radius: 20px; max-width: 900px; margin: 0 auto;">
            <h2 style="text-align: center; color: #333;">⚡ Trading Bot Results</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">
                
                <div style="background: linear-gradient(45deg, #4ecdc4, #44a08d); color: white; padding: 25px; border-radius: 15px;">
                    <h3 style="margin: 0 0 15px 0;">📊 Sentiment Analysis</h3>
                    <p style="margin: 5px 0; font-size: 16px;">
                        <strong>Positive:</strong> {results.get('pos_count', 0)}<br>
                        <strong>Negative:</strong> {results.get('neg_count', 0)}<br>
                        <strong>Neutral:</strong> {results.get('neu_count', 0)}
                    </p>
                    <p style="margin: 15px 0 0 0; font-size: 18px; font-weight: bold;">
                        📈 Score: {results.get('sentiment_score', 0):.4f}
                    </p>
                </div>
                
                <div style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 25px; border-radius: 15px;">
                    <h3 style="margin: 0 0 15px 0;">🔮 Price Prediction</h3>
                    <p style="margin: 5px 0; font-size: 18px;">
                        <strong>Predicted:</strong><br>
                        ${results.get('predicted_price', 0):,.2f}
                    </p>
                    <p style="margin: 15px 0 0 0; font-size: 18px;">
                        <strong>Current:</strong><br>
                        ${results.get('btc_price', 0):,.2f}
                    </p>
                </div>
                
                <div style="background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; padding: 25px; border-radius: 15px;">
                    <h3 style="margin: 0 0 15px 0;">📢 Trading Decision</h3>
                    <p style="margin: 5px 0; font-size: 24px; font-weight: bold;">
                        {results.get('action', 'UNKNOWN')}
                    </p>
                    <p style="margin: 15px 0 0 0; font-size: 16px;">
                        Email: {'✅ Sent' if results.get('email_sent', False) else '❌ Not sent'}
                    </p>
                </div>
                
                <div style="background: linear-gradient(45deg, #2ecc71, #27ae60); color: white; padding: 25px; border-radius: 15px;">
                    <h3 style="margin: 0 0 15px 0;">💰 Portfolio Status</h3>
                    <p style="margin: 5px 0; font-size: 16px;">
                        <strong>USD Balance:</strong><br>
                        ${results.get('usd_balance', 0):,.2f}
                    </p>
                    <p style="margin: 15px 0 0 0; font-size: 16px;">
                        <strong>BTC Balance:</strong><br>
                        {results.get('btc_balance', 0):.6f} BTC
                    </p>
                </div>
                
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h4 style="color: #333; margin: 0 0 10px 0;">📋 Summary</h4>
                <p style="color: #666; margin: 0; line-height: 1.6;">
                    Analysis completed at {results.get('timestamp', 'Unknown time')}. 
                    The bot analyzed sentiment from {results.get('total_posts', 'multiple')} Reddit posts across 5 crypto subreddits, 
                    made an AI-powered price prediction, and executed a <strong>{results.get('action', 'UNKNOWN')}</strong> decision.
                    {'Email alert was sent to notify you of this action.' if results.get('email_sent', False) else 'No email alert was necessary for this action.'}
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">← Back to Dashboard</a>
                <a href="/status" style="background: #28a745; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">📊 System Status</a>
                <a href="https://docs.google.com/spreadsheets/d/1whYmmYjQTddVyLiHJxuQl_95rXQPC2yvlrq5yP32JFo/edit" target="_blank" style="background: #764ba2; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">📋 View Google Sheet</a>
            </div>
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

@app.route("/results")
def view_latest_results():
    global last_run_results
    if not last_run_results:
        return """
        <div style="text-align: center; padding: 50px; font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
            <div style="background: white; padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
                <h2>📊 No Results Yet</h2>
                <p>Run the bot first to see detailed results!</p>
                <a href="/run-once" style="background: #28a745; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; margin: 10px;">⚡ Run Bot Once</a>
                <a href="/" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none;">← Back to Dashboard</a>
            </div>
        </div>
        """
    
    # Redirect to the same results display as run-once
    return run_once()

def run_trading_bot_wrapper():
    """Wrapper to handle bot state"""
    global bot_running
    try:
        run_trading_bot()
    finally:
        bot_running = False

def run_trading_bot_with_results():
    """Enhanced version that returns detailed results"""
    from trading_bot import (
        download_model_from_github, download_scaler_from_github,
        get_sentiment_score, get_historical_btc_prices, get_real_btc_price,
        predict_next_day_price, setup_google_sheets, add_headers_if_needed,
        log_trade_to_google_sheets, send_email_alert
    )
    import pickle
    import numpy as np
    
    # Download required files
    model_downloaded = download_model_from_github()
    scaler_downloaded = download_scaler_from_github()
    
    # Load model and scaler
    try:
        if 'load_model' in globals() and model_downloaded:
            from tensorflow.keras.models import load_model
            model = load_model("btc_lstm_model.h5")
        else:
            model = None
    except:
        model = None
    
    try:
        if scaler_downloaded and os.path.exists("scaler.pkl"):
            with open("scaler.pkl", "rb") as f:
                scaler = pickle.load(f)
        else:
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()
            dummy_data = np.array([[30000], [70000]])
            scaler.fit(dummy_data)
    except:
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        dummy_data = np.array([[30000], [70000]])
        scaler.fit(dummy_data)
    
    # Setup Google Sheets
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise Exception("GOOGLE_SHEET_ID not found in environment variables!")
    
    sheet = setup_google_sheets("credintial.json", sheet_id, "trading_bot_log")
    add_headers_if_needed(sheet)
    
    # Get sentiment analysis
    sentiment_score, pos, neg, neu = get_sentiment_score()
    total_posts = pos + neg + neu
    
    # Get price data and make prediction
    historical_prices = get_historical_btc_prices()
    predicted_price = predict_next_day_price(model, scaler, historical_prices, 60)
    btc_price = get_real_btc_price()
    
    # Trading logic
    usd_balance = 1000.0
    btc_balance = 0.0
    average_buy_price = 0.0
    action = "HOLD"
    email_sent = False
    
    if sentiment_score > 0.3 and predicted_price > btc_price * 1.01 and usd_balance >= 100:
        action = "BUY"
        btc_bought = 100 / btc_price
        usd_balance -= 100
        btc_balance += btc_bought
        average_buy_price = ((average_buy_price * (btc_balance - btc_bought)) + (btc_price * btc_bought)) / btc_balance
    elif sentiment_score < -0.3 and predicted_price < btc_price * 0.99 and btc_balance >= 0.001:
        action = "SELL"
        usd_gained = 0.001 * btc_price
        btc_balance -= 0.001
        usd_balance += usd_gained
        if btc_balance == 0:
            average_buy_price = 0.0
    elif btc_balance >= 0.001:
        if btc_price <= average_buy_price * 0.95:
            action = "STOP-LOSS"
            usd_gained = 0.001 * btc_price
            btc_balance -= 0.001
            usd_balance += usd_gained
        elif btc_price >= average_buy_price * 1.10:
            action = "TAKE-PROFIT"
            usd_gained = 0.001 * btc_price
            btc_balance -= 0.001
            usd_balance += usd_gained
    
    # Log to file and Google Sheets
    with open("sentiment_trade_log.txt", "a") as f:
        f.write(f"{datetime.now()} | Action: {action} | Sentiment: {sentiment_score:.4f} | Predicted BTC: ${predicted_price:.2f} | BTC: ${btc_price:.2f} | USD: ${usd_balance:.2f} | BTC Bal: {btc_balance:.6f}\n")
    
    log_trade_to_google_sheets(sheet, action, sentiment_score, predicted_price, btc_price, usd_balance, btc_balance)
    
    # Send email for significant actions
    if action in ["BUY", "SELL", "STOP-LOSS", "TAKE-PROFIT"]:
        try:
            send_email_alert(
                f"[Crypto Bot] {action} Signal",
                f"Action: {action}\nSentiment: {sentiment_score:.4f}\nPredicted: ${predicted_price:.2f}\nBTC Now: ${btc_price:.2f}\nUSD Balance: ${usd_balance:.2f}\nBTC Balance: {btc_balance:.6f}"
            )
            email_sent = True
        except:
            email_sent = False
    
    # Return detailed results
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sentiment_score": sentiment_score,
        "pos_count": pos,
        "neg_count": neg,
        "neu_count": neu,
        "total_posts": total_posts,
        "predicted_price": predicted_price,
        "btc_price": btc_price,
        "action": action,
        "usd_balance": usd_balance,
        "btc_balance": btc_balance,
        "email_sent": email_sent
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
