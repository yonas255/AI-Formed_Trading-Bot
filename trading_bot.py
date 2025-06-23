import os
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

load_dotenv()  # Load env vars from .env

MODEL_PATH = "btc_lstm_model.h5"
SCALER_PATH = "scaler.pkl"
JSON_KEYFILE = "credintial.json"

def download_model_from_github():
    if not os.path.exists(MODEL_PATH):
        print("📥 Downloading LSTM model from GitHub...")
        try:
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
    if not os.path.exists(SCALER_PATH):
        print("📥 Downloading scaler from GitHub...")
        try:
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
    from sklearn.preprocessing import MinMaxScaler
    mock_scaler = MinMaxScaler()
    dummy_data = np.array([[30000], [70000]])
    mock_scaler.fit(dummy_data)
    return mock_scaler

def setup_google_sheets(json_keyfile_path, sheet_id, worksheet_name="Sheet1"):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(creds)
    
    # Try to access the worksheet, if it doesn't exist, create it
    try:
        sheet = client.open_by_key(sheet_id)
        try:
            worksheet = sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            print(f"Worksheet '{worksheet_name}' not found, creating it...")
            worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
        return worksheet
    except Exception as e:
        print(f"Error accessing Google Sheet: {e}")
        raise

def add_headers_if_needed(sheet):
    if not sheet.row_values(1):
        sheet.append_row([
            "Timestamp", "Action", "Sentiment Score", "Predicted BTC Price",
            "BTC Price (USD)", "USD Balance", "BTC Balance"
        ])

def log_trade_to_google_sheets(sheet, action, sentiment_score, predicted_price,
                               btc_price, usd_balance, btc_balance):
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action,
        f"{sentiment_score:.4f}", f"{predicted_price:.2f}", f"{btc_price:.2f}",
        f"{usd_balance:.2f}", f"{btc_balance:.6f}"
    ]
    sheet.append_row(row)

def send_email_alert(subject, content):
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        message = Mail(
            from_email=os.getenv("ALERT_EMAIL_FROM"),
            to_emails=os.getenv("ALERT_EMAIL_TO"),
            subject=subject,
            plain_text_content=content
        )
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
    for sub in [
        "Bitcoin", "CryptoCurrency", "CryptoMarkets", "Ethereum", "CryptoMoonShots"
    ]:
        for post in reddit.subreddit(sub).hot(limit=100):
            if not post.stickied:
                score = analyzer.polarity_scores(post.title)["compound"]
                if score >= 0.05:
                    pos += 1
                elif score <= -0.05:
                    neg += 1
                else:
                    neu += 1
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
        return requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"}
        ).json()['bitcoin']['usd']
    except:
        return 65000

def predict_next_day_price(model, scaler, recent_prices, look_back=60):
    if model is None:
        current_price = recent_prices.iloc[-1]
        import random
        variation = random.uniform(-0.05, 0.05)
        return current_price * (1 + variation)

    try:
        last_sequence = scaler.transform(
            recent_prices[-look_back:].values.reshape(-1, 1))
        X_test = np.array([last_sequence.flatten()]).reshape(1, look_back, 1)
        prediction = model.predict(X_test)
        return scaler.inverse_transform(prediction)[0][0]
    except Exception as e:
        print(f"⚠️ Prediction error: {e} - using mock prediction")
        current_price = recent_prices.iloc[-1]
        import random
        variation = random.uniform(-0.05, 0.05)
        return current_price * (1 + variation)

def run_trading_bot():
    model_downloaded = download_model_from_github()
    scaler_downloaded = download_scaler_from_github()

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
    
    # Check if Google Sheet ID is configured
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("❌ GOOGLE_SHEET_ID not found in environment variables!")
        print("Please add your Google Sheet ID to the Secrets tab in Replit.")
        return
    
    try:
        sheet = setup_google_sheets(JSON_KEYFILE, sheet_id, "trading_bot_log")
        add_headers_if_needed(sheet)
        print("✅ Google Sheets connected successfully!")
    except Exception as e:
        print(f"❌ Google Sheets connection failed: {e}")
        print("Please check your GOOGLE_SHEET_ID and make sure the sheet exists.")
        return

    usd_balance = 1000.0
    btc_balance = 0.0
    average_buy_price = 0.0
    historical_prices = get_historical_btc_prices()

    # Single execution - no loop needed for cronjob
    sentiment_score, pos, neg, neu = get_sentiment_score()
    predicted_price = predict_next_day_price(model, scaler, historical_prices, look_back)
    btc_price = get_real_btc_price()

    action = "HOLD"
    
    # Calculate market indicators for realistic trading
    price_change_pct = (predicted_price - btc_price) / btc_price if predicted_price > 0 else 0
    
    # Enhanced multi-factor scoring system with equal weight for buy/sell
    buy_signals = 0
    sell_signals = 0
    buy_strength = 0.0
    sell_strength = 0.0
    
    # More realistic sentiment scoring with lower thresholds
    if sentiment_score > 0.3:  # Strong positive sentiment
        buy_signals += 2
        buy_strength += 0.4
    elif sentiment_score > 0.15:  # Moderate positive sentiment
        buy_signals += 1
        buy_strength += 0.2
    elif sentiment_score < -0.15:  # Moderate negative sentiment
        sell_signals += 1
        sell_strength += 0.2
    elif sentiment_score < -0.3:  # Strong negative sentiment
        sell_signals += 2
        sell_strength += 0.4
    
    # Enhanced price prediction scoring with realistic thresholds
    if price_change_pct > 0.02:  # 2% predicted gain
        buy_signals += 2
        buy_strength += 0.3
    elif price_change_pct > 0.008:  # 0.8% predicted gain
        buy_signals += 1
        buy_strength += 0.15
    elif price_change_pct < -0.008:  # 0.8% predicted drop
        sell_signals += 1
        sell_strength += 0.15
    elif price_change_pct < -0.02:  # 2% predicted drop
        sell_signals += 2
        sell_strength += 0.3
    
    # Market momentum analysis (using recent price changes)
    recent_momentum = (btc_price - historical_prices.iloc[-5:].mean()) / historical_prices.iloc[-5:].mean()
    if recent_momentum > 0.015:  # Strong upward momentum
        buy_signals += 1
        buy_strength += 0.2
    elif recent_momentum < -0.015:  # Strong downward momentum
        sell_signals += 1
        sell_strength += 0.2
    
    # Enhanced position management with realistic profit targets
    if btc_balance > 0 and average_buy_price > 0:
        current_profit_pct = (btc_price - average_buy_price) / average_buy_price
        
        # Profit taking with graduated selling
        if current_profit_pct > 0.08:  # 8% profit - start taking profits
            sell_signals += 2
            sell_strength += 0.3
        elif current_profit_pct > 0.04:  # 4% profit - consider selling
            sell_signals += 1
            sell_strength += 0.15
        elif current_profit_pct < -0.04:  # 4% loss - risk management
            sell_signals += 1
            sell_strength += 0.2
        elif current_profit_pct < -0.07:  # 7% loss - cut losses
            sell_signals += 2
            sell_strength += 0.4
    
    # Market fear assessment (simulate VIX-like indicator)
    price_volatility = historical_prices.rolling(10).std().iloc[-1] / historical_prices.rolling(10).mean().iloc[-1]
    if price_volatility > 0.04:  # High volatility - be cautious
        if buy_signals > sell_signals:
            buy_strength *= 0.7  # Reduce buy confidence in volatile markets
        else:
            sell_strength *= 1.2  # Increase sell urgency in volatile markets
    
    # Calculate total signal strength
    total_buy_strength = buy_signals * 0.3 + buy_strength
    total_sell_strength = sell_signals * 0.3 + sell_strength
    
    # Enhanced position sizing with risk management
    max_position_pct = 0.10  # 10% max per trade
    position_size = min(usd_balance * max_position_pct, 120)  # Max $120 per trade
    
    # More balanced execution thresholds
    if total_buy_strength >= 1.0 and usd_balance >= position_size and position_size >= 50:
        # Dynamic position sizing based on signal strength
        confidence_multiplier = min(total_buy_strength / 2.0, 1.0)
        actual_position = position_size * confidence_multiplier
        
        action = "BUY"
        btc_bought = actual_position / btc_price
        usd_balance -= actual_position
        btc_balance += btc_bought
        
        # Update average buy price
        if btc_balance > btc_bought:
            total_invested = (btc_balance - btc_bought) * average_buy_price + actual_position
            average_buy_price = total_invested / btc_balance
        else:
            average_buy_price = btc_price
            
    elif total_sell_strength >= 1.0 and btc_balance >= 0.0005:
        # Graduated selling based on signal strength and profit levels
        if btc_balance > 0 and average_buy_price > 0:
            current_profit_pct = (btc_price - average_buy_price) / average_buy_price
            
            # Sell percentage based on signal strength and profit
            if current_profit_pct > 0.06:  # Good profit
                sell_ratio = min(0.5, total_sell_strength / 2.0)  # Sell up to 50%
            elif current_profit_pct > 0.02:  # Small profit
                sell_ratio = min(0.3, total_sell_strength / 2.5)  # Sell up to 30%
            elif current_profit_pct < -0.05:  # Loss cutting
                sell_ratio = min(0.6, total_sell_strength / 1.5)  # Sell up to 60%
            else:  # Neutral territory
                sell_ratio = min(0.25, total_sell_strength / 3.0)  # Sell up to 25%
        else:
            sell_ratio = min(0.3, total_sell_strength / 2.0)
        
        sell_amount = btc_balance * sell_ratio
        action = "SELL"
        usd_gained = sell_amount * btc_price
        btc_balance -= sell_amount
        usd_balance += usd_gained
        
        # Reset average buy price if position is closed
        if btc_balance <= 0.00001:
            btc_balance = 0
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

    # Enhanced logging with signal analysis
    with open("sentiment_trade_log.txt", "a") as f:
        f.write(f"{datetime.utcnow()} | Action: {action} | Sentiment: {sentiment_score:.4f} | "
               f"Buy Signals: {buy_signals} (Strength: {total_buy_strength:.2f}) | "
               f"Sell Signals: {sell_signals} (Strength: {total_sell_strength:.2f}) | "
               f"Predicted: ${predicted_price:.2f} | Current: ${btc_price:.2f} | "
               f"USD: ${usd_balance:.2f} | BTC: {btc_balance:.6f} | "
               f"Profit: {((btc_price - average_buy_price) / average_buy_price * 100) if average_buy_price > 0 else 0:.2f}%\n")

    log_trade_to_google_sheets(sheet, action, sentiment_score, predicted_price, btc_price, usd_balance, btc_balance)

    if action in ["BUY", "SELL", "STOP-LOSS", "TAKE-PROFIT"]:
        send_email_alert(
            f"[Crypto Bot] {action} Signal",
            f"Action: {action}\nSentiment: {sentiment_score:.4f}\nPredicted: ${predicted_price:.2f}\nBTC Now: ${btc_price:.2f}\nUSD Balance: ${usd_balance:.2f}\nBTC Balance: {btc_balance:.6f}"
        )

    print(f"✅ Trading cycle completed: {action} | Sentiment: {sentiment_score:.4f} | BTC: ${btc_price:.2f}")
