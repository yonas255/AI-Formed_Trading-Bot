AI-Powered Crypto Trading Bot
An advanced AI-powered cryptocurrency trading simulation bot that combines Reddit sentiment analysis, LSTM-based price predictions, and sophisticated technical indicators to make intelligent trading decisions. This project features a real-time web dashboard, multiple AI models, and comprehensive logging capabilities.

Features
 AI & Machine Learning
LSTM Price Prediction: Advanced neural networks for Bitcoin price forecasting
Ensemble Models: Multiple AI models (LSTM, GRU, CNN-LSTM, Deep LSTM) working together
Sentiment Analysis: Real-time Reddit sentiment analysis using VADER
Technical Indicators: RSI, MACD, Bollinger Bands, Fear & Greed Index

 Real-Time Dashboard
Interactive Charts: Live price charts with technical analysis
Multi-Crypto Support: BTC, ETH, ADA, SOL, BNB tracking
WebSocket Updates: Real-time data streaming
Dark/Light Theme: Toggle between themes
Mobile Responsive: Works on all devices

 Trading Features
Risk Management: Stop-loss and take-profit automation
Position Sizing: Dynamic position calculation based on signal strength
Portfolio Tracking: Real-time balance and P&L monitoring
Trading Signals: Multi-factor signal generation

 Analysis & Monitoring
Google Sheets Integration: Automatic trade logging
Email Alerts: SendGrid integration for trade notifications
automation: Works with Cron-Job.org. runs by it self 5 times in 24 hours.
Confidence Reports: Model performance and reliability metrics
Backtesting: Historical performance validation

 Technology Stack
Backend: Python, Flask, Flask-SocketIO
AI/ML: TensorFlow, Keras, scikit-learn
APIs: Reddit (PRAW), CoinGecko, CryptoCompare, Binance
Database: Google Sheets, SQL support
Frontend: HTML5, Chart.js, WebSockets
Deployment: Replit (Production ready)

 Quick Start
1. Clone & Setup
git clone <your-repo-url>
cd crypto-trading-bot

2. Environment Variables
Set up the following secrets in Replit's Secrets tab:

Required:
REDDIT_CLIENT_ID - Reddit API client ID
REDDIT_CLIENT_SECRET - Reddit API client secret
REDDIT_USER_AGENT - Reddit API user agent
GOOGLE_SHEET_ID - Your Google Sheets ID

Optional:
SENDGRID_API_KEY - For email alerts
ALERT_EMAIL_FROM - Sender email
ALERT_EMAIL_TO - Recipient email

3. Google Sheets Setup
Create a Google Sheet for trade logging
Share it with: trading-bot-logger@trading-bot-project-460614.iam.gserviceaccount.com
Give "Editor" permissions
Copy the Sheet ID to GOOGLE_SHEET_ID secret

4. Automation (Optional)
   
 Use https://cron-job.org to ping this URL every 4 hours:
  https://<your-replit-username>.replit.app/run
  
6. Run the Application
Click the Run button in Replit or use:
python3 app.py
 
 Usage
Dashboard Access
Main Dashboard: https://your-repl-name.replit.app/
Trading Endpoint: https://your-repl-name.replit.app/run
Status Check: https://your-repl-name.replit.app/status

Bot Controls
 Start Bot: Continuous trading mode
 Run Once: Single analysis and trade decision
 Stop Bot: Stop continuous trading
 Status: Check system health
 Confidence Report: View model performance
 
Multi-Crypto Support
Switch between cryptocurrencies in the dashboard:

Bitcoin (BTC)
Ethereum (ETH)
Cardano (ADA)
Solana (SOL)
Binance Coin (BNB)


 AI Models
 
Enhanced LSTM Model
Features: 50+ technical indicators
Architecture: Multi-layer LSTM with dropout
Training: Historical price data with technical analysis

Ensemble Models
LSTM: Basic long short-term memory
GRU: Gated recurrent unit variant
CNN-LSTM: Convolutional + LSTM hybrid
Deep LSTM: Multi-layer deep architecture

Model Training

# Train enhanced model. Run:
python3 enhanced_model_trainer.py

# Train ensemble models. Run:
python3 model_ensemble.py

# Run backtesting. Run:
python3 backtest_bot.py
 
 
 API Integrations
 
Price Data Sources
CryptoCompare: Primary price feed
Binance: Secondary price source
CoinCap: Backup price data
CoinGecko: Historical data (rate limited)


Sentiment Analysis
Reddit: 6 crypto subreddits monitored
VADER: Sentiment intensity analysis
Real-time: Continuous sentiment tracking


Technical Analysis
RSI: Relative Strength Index
MACD: Moving Average Convergence Divergence
Bollinger Bands: Price volatility bands
Fear & Greed Index: Market sentiment indicator


 Configuration

Trading Parameters
# Risk Management
max_position_size = 0.15  # 15% max per trade
stop_loss_pct = 0.05     # 5% stop loss
take_profit_pct = 0.15   # 15% take profit

# Signal Thresholds
sentiment_threshold = 0.2  # Sentiment signal strength
rsi_oversold = 30         # RSI oversold level
rsi_overbought = 70       # RSI overbought level


Model Configuration

# LSTM Parameters
look_back = 60           # Historical data points
epochs = 100            # Training epochs
batch_size = 32         # Training batch size
 
 
Performance Monitoring

Confidence Reports

Access detailed performance metrics:
Model accuracy validation
API reliability status
Deployment readiness
Risk assessment


Backtesting

Historical performance validation:
Strategy returns
Win/loss ratios
Maximum drawdown
Sharpe ratio


Live Monitoring

Google Sheets logging
Email trade alerts
Real-time dashboard
WebSocket updates


Deployment

Replit Deployment:
1. Configure: Set up all environment variables
2. Test: Run confidence report to verify setup
3. Deploy: Click the "Deploy" button in Replit
4. Monitor: Use the dashboard to track performance


Production Features

Auto-scaling: Handles traffic spikes
WebSocket Support: Real-time updates
Mobile Responsive: Works on all devices
Error Handling: Graceful API fallbacks


 Project Structure
├── app.py                      # Main Flask application
├── trading_bot.py              # Core trading logic
├── enhanced_trading_bot.py     # Advanced trading features
├── enhanced_model_trainer.py   # AI model training
├── model_ensemble.py           # Ensemble model management
├── backtest_bot.py            # Historical backtesting
├── test_bot_accuracy.py       # Model validation
├── requirements.txt           # Python dependencies
├── main.py                    # Original simple version
└── *.h5, *.pkl               # Trained models and scalers


⚠ Important Notes

Disclaimer
This is a simulation project for educational purposes only. It does not perform real cryptocurrency transactions. Always:

Test thoroughly before any real trading
Start with small amounts
Understand the risks involved
Use proper risk management


Rate Limits

APIs have rate limits (respected automatically)
Cached data reduces API calls
Multiple fallback sources prevent failures


Security
All API keys stored in Replit Secrets
No sensitive data in code
Secure Google Sheets integration


Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

   
License
This project is for educational purposes. Use responsibly and at your own risk.

Support
If you encounter issues:

1. Check the /status endpoint for system health
2. Review the /confidence-report for setup validation
3. Verify all environment variables are set
4. Check Google Sheets permissions

   
Future Enhancements

 Additional cryptocurrencies
 More AI models (Transformers, etc.)
 Advanced portfolio management
 Social sentiment from Twitter
 Options trading simulation
 Mobile app development

Author

 Built by Yonas Haf, as part of the Academic Internship Project 2025
If you like it, ⭐ star this repo.
