import os
import threading
from flask import Flask
import time
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
try:
    from tensorflow.keras.models import load_model
except ImportError:
    print("TensorFlow not installed - using mock prediction")
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import praw
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()
print("🔍 Reddit Client ID:", os.getenv("REDDIT_CLIENT_ID"))


MODEL_PATH = "btc_lstm_model.h5"
SCALER_PATH = "scaler.pkl"
JSON_KEYFILE = "credintial.json"

def download_model_from_github():
    """Download the LSTM model file from GitHub if it doesn't exist locally."""
    if not os.path.exists(MODEL_PATH):
        print("📥 Downloading LSTM model from GitHub...")
        try:
            # Replace with your actual GitHub raw file URL
            model_url = "https://github.com/yonas255/bot-files/raw/d85a362794a87a4ce0050f9e145664159b107da9/btc_lstm_model.h5"
            response = requests.get(model_url, stream=True)
            response.raise_for_status()

            with open(MODEL_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("✅ Model downloaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to download model: {e}")
            return False
    else:
        print("✅ Model file already exists locally")
        return True

def download_scaler_from_github():
    """Download the scaler file from GitHub if it doesn't exist locally."""
    if not os.path.exists(SCALER_PATH):
        print("📥 Downloading scaler from GitHub...")
        try:
            # Replace with your actual GitHub raw file URL for scaler
            scaler_url = "https://github.com/yonas255/bot-files/raw/d85a362794a87a4ce0050f9e145664159b107da9/scaler.pkl"
            response = requests.get(scaler_url, stream=True)
            response.raise_for_status()

            with open(SCALER_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("✅ Scaler downloaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to download scaler: {e}")
            return False
    else:
        print("✅ Scaler file already exists locally")
        return True

def create_mock_scaler():
    """Create a mock scaler for fallback when real scaler is not available."""
    from sklearn.preprocessing import MinMaxScaler
    mock_scaler = MinMaxScaler()
    # Fit with some dummy data to make it functional
    dummy_data = np.array([[30000], [70000]])  # Rough BTC price range
    mock_scaler.fit(dummy_data)
    return mock_scaler

def setup_google_sheets(json_keyfile_path, sheet_id, worksheet_name="Sheet1"):
     scope = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
     creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
     client = gspread.authorize(creds)
     return client.open_by_key(sheet_id).worksheet(worksheet_name)

def add_headers_if_needed(sheet):
     if not sheet.row_values(1):
         sheet.append_row(["Timestamp", "Action", "Sentiment Score", "Predicted BTC Price", "BTC Price (USD)", "USD Balance", "BTC Balance"])

def log_trade_to_google_sheets(sheet, action, sentiment_score, predicted_price, btc_price, usd_balance, btc_balance):
     row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, f"{sentiment_score:.4f}", f"{predicted_price:.2f}", f"{btc_price:.2f}", f"{usd_balance:.2f}", f"{btc_balance:.6f}"]
     sheet.append_row(row)

def send_email_alert(subject, content):
     try:
         sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
         message = Mail(from_email=os.getenv("ALERT_EMAIL_FROM"), to_emails=os.getenv("ALERT_EMAIL_TO"), subject=subject, plain_text_content=content)
         sg.send(message)
     except Exception as e:
         print(f"Email failed: {e}")

reddit = praw.Reddit(
     client_id=os.getenv("REDDIT_CLIENT_ID"),
     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
     user_agent=os.getenv("REDDIT_USER_AGENT")
 )
analyzer = SentimentIntensityAnalyzer()

def get_sentiment_score():
     pos, neg, neu = 0, 0, 0
     for sub in ["Bitcoin", "CryptoCurrency", "CryptoMarkets", "Ethereum", "CryptoMoonShots"]:
         for post in reddit.subreddit(sub).hot(limit=100):
             if not post.stickied:
                 score = analyzer.polarity_scores(post.title)["compound"]
                 if score >= 0.05: pos += 1
                 elif score <= -0.05: neg += 1
                 else: neu += 1
     total = pos + neg + neu
     return ((pos - neg) / total if total > 0 else 0), pos, neg, neu

def get_historical_btc_prices(days=180):
     url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
     data = requests.get(url, params={"vs_currency": "usd", "days": days}).json()
     df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
     df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
     df.set_index('date', inplace=True)
     return df['price']

def get_real_btc_price():
     try:
         return requests.get("https://api.coingecko.com/api/v3/simple/price", params={"ids": "bitcoin", "vs_currencies": "usd"}).json()['bitcoin']['usd']
     except:
         return 65000

def predict_next_day_price(model, scaler, recent_prices, look_back=60):
     if model is None:
         # Mock prediction when model is not available
         current_price = recent_prices.iloc[-1]
         # Simple mock: add small random variation
         import random
         variation = random.uniform(-0.05, 0.05)  # ±5% variation
         return current_price * (1 + variation)

     try:
         last_sequence = scaler.transform(recent_prices[-look_back:].values.reshape(-1,1))
         X_test = np.array([last_sequence.flatten()]).reshape(1, look_back, 1)
         prediction = model.predict(X_test)
         return scaler.inverse_transform(prediction)[0][0]
     except Exception as e:
         print(f"⚠️ Prediction error: {e} - using mock prediction")
         current_price = recent_prices.iloc[-1]
         import random
         variation = random.uniform(-0.05, 0.05)
         return current_price * (1 + variation)

def run_bot():
     # Download model from GitHub if needed
     model_downloaded = download_model_from_github()
     scaler_downloaded = download_scaler_from_github()

     # Handle missing model files gracefully
     try:
         if 'load_model' in globals() and model_downloaded:
             model = load_model(MODEL_PATH)
             print("✅ Model loaded successfully!")
         else:
             model = None
             print("⚠️ TensorFlow not available - using mock predictions")
     except Exception as e:
         model = None
         print(f"⚠️ Model file error: {e} - using mock predictions")

     # Handle missing scaler file gracefully
     try:
         if scaler_downloaded and os.path.exists(SCALER_PATH):
             with open(SCALER_PATH, "rb") as f:
                 scaler = pickle.load(f)
             print("✅ Scaler loaded successfully!")
         else:
             scaler = create_mock_scaler()
             print("⚠️ Using mock scaler - predictions may be inaccurate")
     except Exception as e:
         scaler = create_mock_scaler()
         print(f"⚠️ Scaler file error: {e} - using mock scaler")
     look_back = 60
     sheet = setup_google_sheets(JSON_KEYFILE, os.getenv("GOOGLE_SHEET_ID"))
     add_headers_if_needed(sheet)

     usd_balance = 1000.0
     btc_balance = 0.0
     average_buy_price = 0.0
     historical_prices = get_historical_btc_prices()

     sentiment_history = []
     predicted_history = []
     live_price_history = []

     for run in range(6):
         sentiment_score, pos, neg, neu = get_sentiment_score()
         predicted_price = predict_next_day_price(model, scaler, historical_prices, look_back)
         btc_price = get_real_btc_price()

         sentiment_history.append(sentiment_score)
         predicted_history.append(predicted_price)
         live_price_history.append(btc_price)

         action = "HOLD"
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
             if btc_balance == 0: average_buy_price = 0.0
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

         with open("sentiment_trade_log.txt", "a") as f:
             f.write(f"{datetime.utcnow()} | Action: {action} | Sentiment: {sentiment_score:.4f} | Predicted BTC: ${predicted_price:.2f} | BTC: ${btc_price:.2f} | USD: ${usd_balance:.2f} | BTC Bal: {btc_balance:.6f}\n")

         log_trade_to_google_sheets(sheet, action, sentiment_score, predicted_price, btc_price, usd_balance, btc_balance)

         if action in ["BUY", "SELL"]:
             send_email_alert(f"[Crypto Bot] {action} Signal", f"Action: {action}\nSentiment: {sentiment_score:.4f}\nPredicted: ${predicted_price:.2f}\nBTC Now: ${btc_price:.2f}")

         if run < 5:
             time.sleep(10)

     plt.figure(figsize=(12, 6))
     plt.plot(sentiment_history, label="Sentiment Score", marker='o')
     plt.plot(predicted_history, label="Predicted BTC Price", linestyle='--')
     plt.plot(live_price_history, label="Live BTC Price", linestyle='-.')
     plt.title("Crypto Bot Sentiment & Price Predictions")
     plt.xlabel("Run Number")
     plt.ylabel("Value")
     plt.legend()
     plt.grid(True)
     plt.tight_layout()
     plt.savefig("run_results_chart.png")
     print("✅ All runs completed. Chart saved as 'run_results_chart.png'")

@app.route("/status")
def status():
     return f"""
     <h2>Bot Status</h2>
     <p>Reddit Client ID: {'✅ Set' if os.getenv('REDDIT_CLIENT_ID') else '❌ Missing'}</p>
     <p>Model file: {'✅ Found' if os.path.exists(MODEL_PATH) else '❌ Missing (will download from GitHub)'}</p>
     <p>Scaler file: {'✅ Found' if os.path.exists(SCALER_PATH) else '❌ Missing'}</p>
     <p>Credentials: {'✅ Found' if os.path.exists(JSON_KEYFILE) else '❌ Missing'}</p>
     <p><a href="/download-model">Download Model Manually</a></p>
     """

@app.route("/download-model")
def manual_download():
     success = download_model_from_github()
     if success:
         return "✅ Model downloaded successfully! <a href='/status'>Check Status</a>"
     else:
         return "❌ Failed to download model. Please check the GitHub URL. <a href='/status'>Check Status</a>"

@app.route("/")
def trigger_bot():
     threading.Thread(target=run_bot).start()
     return """
     <h1>🚀 Crypto Trading Bot</h1>
     <p>✅ Bot has been started successfully!</p>
     <p><a href="/status">Check Bot Status</a></p>
     <p><a href="/download-model">Download Model</a></p>
     <hr>
     <p><em>Bot is now running in the background and will complete 6 trading cycles.</em></p>
     """

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)