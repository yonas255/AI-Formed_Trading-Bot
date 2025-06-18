# AI-Formed_Crypto_Trading-Bot

This project is an AI-powered cryptocurrency trading simulation bot that uses Reddit sentiment analysis and LSTM-based BTC price predictions to simulate intelligent BUY/SELL decisions. The bot scrapes live data from Reddit and CoinGecko, analyzes sentiment using VADER, predicts BTC price using a pre-trained LSTM model (trained in Google Colab), and logs simulated trades into Google Sheets while sending alerts via SendGrid. The trading logic is hosted and automated via Flask on Replit. This is a simulation project intended for academic and learning purposes only — it does not perform real transactions.

How to Install

1. Clone the repository.

2. Upload your .env file with the required API keys (Reddit, SendGrid, etc.).

3. Upload scaler.pkl and btc_lstm_model.h5 from the Colab-trained model.

4. Run pip install -r requirements.txt to install dependencies.

5. Launch the Flask server (python trading_bot.py).

To simulate storing trade logs in a local SQL database, use the provided create_trades_table.sql script to initialize a trades table. You can run this with any SQL-compatible tool like SQLite or PostgreSQL.
