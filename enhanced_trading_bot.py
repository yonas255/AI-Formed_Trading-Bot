
import os
import time
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import requests
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import gspread
from oauth2client.service_account import ServiceAccountCredentials

try:
    from tensorflow.keras.models import load_model
    import ta
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'tensorflow', 'ta'])
    from tensorflow.keras.models import load_model
    import ta

class EnhancedTradingBot:
    def __init__(self):
        self.model = None
        self.feature_scaler = None
        self.price_scaler = None
        self.feature_names = []
        self.load_enhanced_model()
        
        # Portfolio state
        self.usd_balance = 1000.0
        self.btc_balance = 0.0
        self.average_buy_price = 0.0
        
        # Risk management
        self.max_position_size = 0.1  # 10% max per trade
        self.stop_loss_pct = 0.05     # 5% stop loss
        self.take_profit_pct = 0.15   # 15% take profit
        
        # Setup external services
        self.setup_reddit()
        self.setup_sentiment_analyzer()
        
    def load_enhanced_model(self):
        """Load the enhanced model and scalers"""
        try:
            if os.path.exists('btc_enhanced_lstm_model.h5'):
                self.model = load_model('btc_enhanced_lstm_model.h5')
                print("✅ Enhanced LSTM model loaded")
            else:
                print("⚠️ Enhanced model not found, using basic model")
                if os.path.exists('btc_lstm_model.h5'):
                    self.model = load_model('btc_lstm_model.h5')
                
            # Load scalers
            if os.path.exists('enhanced_feature_scaler.pkl'):
                with open('enhanced_feature_scaler.pkl', 'rb') as f:
                    self.feature_scaler = pickle.load(f)
                    
            if os.path.exists('enhanced_price_scaler.pkl'):
                with open('enhanced_price_scaler.pkl', 'rb') as f:
                    self.price_scaler = pickle.load(f)
                    
            if os.path.exists('feature_names.pkl'):
                with open('feature_names.pkl', 'rb') as f:
                    self.feature_names = pickle.load(f)
                    
            print(f"✅ Loaded {len(self.feature_names)} enhanced features")
            
        except Exception as e:
            print(f"⚠️ Error loading enhanced model: {e}")
            self.model = None
    
    def setup_reddit(self):
        """Setup Reddit API connection"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT")
            )
        except Exception as e:
            print(f"⚠️ Reddit setup failed: {e}")
            self.reddit = None
    
    def setup_sentiment_analyzer(self):
        """Setup sentiment analysis"""
        self.analyzer = SentimentIntensityAnalyzer()
    
    def get_enhanced_bitcoin_data(self, days=90):
        """Fetch comprehensive Bitcoin data for analysis"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {"vs_currency": "usd", "days": days, "interval": "daily"}
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Create DataFrame
            df = pd.DataFrame()
            df['timestamp'] = [x[0] for x in data['prices']]
            df['close'] = [x[1] for x in data['prices']]
            df['volume'] = [x[1] for x in data['total_volumes']]
            df['market_cap'] = [x[1] for x in data['market_caps']]
            
            # Generate OHLC approximation
            df['high'] = df['close'] * (1 + np.random.uniform(0, 0.03, len(df)))
            df['low'] = df['close'] * (1 - np.random.uniform(0, 0.03, len(df)))
            df['open'] = df['close'].shift(1).fillna(df['close'])
            
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('date')
            
            return df
            
        except Exception as e:
            print(f"⚠️ Using mock data: {e}")
            return self._generate_mock_data(days)
    
    def _generate_mock_data(self, days):
        """Generate realistic mock data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 65000
        
        prices = []
        volumes = []
        
        for i in range(days):
            daily_return = np.random.normal(0.001, 0.03)
            price = base_price * (1 + daily_return)
            prices.append(price)
            volumes.append(np.random.uniform(500000000, 2000000000))
            base_price = price
        
        df = pd.DataFrame({
            'close': prices,
            'volume': volumes,
            'market_cap': [p * 19000000 for p in prices]
        }, index=dates)
        
        df['high'] = df['close'] * (1 + np.random.uniform(0, 0.03, len(df)))
        df['low'] = df['close'] * (1 - np.random.uniform(0, 0.03, len(df)))
        df['open'] = df['close'].shift(1).fillna(df['close'])
        
        return df
    
    def engineer_features(self, data):
        """Engineer the same features as used in training"""
        df = data.copy()
        
        # Price-based features
        df['price_change'] = df['close'].pct_change()
        df['price_volatility'] = df['price_change'].rolling(window=20).std()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Moving averages
        for period in [7, 14, 30, 50, 100]:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
            df[f'price_to_sma_{period}'] = df['close'] / df[f'sma_{period}']
        
        # Technical indicators
        df['rsi_14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        df['rsi_30'] = ta.momentum.RSIIndicator(df['close'], window=30).rsi()
        
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        bollinger = ta.volatility.BollingerBands(df['close'])
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_lower'] = bollinger.bollinger_lband()
        df['bb_middle'] = bollinger.bollinger_mavg()
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        df['williams_r'] = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close']).williams_r()
        df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
        
        # Volume features
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        df['price_volume'] = df['close'] * df['volume']
        df['obv'] = ta.volume.OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
        
        # Additional indicators
        df['cci'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close']).cci()
        df['roc'] = ta.momentum.ROCIndicator(df['close']).roc()
        df['mfi'] = ta.volume.MFIIndicator(df['high'], df['low'], df['close'], df['volume']).money_flow_index()
        
        ichimoku = ta.trend.IchimokuIndicator(df['high'], df['low'])
        df['ichimoku_a'] = ichimoku.ichimoku_a()
        df['ichimoku_b'] = ichimoku.ichimoku_b()
        
        # Support/Resistance
        df['support'] = df['low'].rolling(window=20).min()
        df['resistance'] = df['high'].rolling(window=20).max()
        df['support_distance'] = (df['close'] - df['support']) / df['close']
        df['resistance_distance'] = (df['resistance'] - df['close']) / df['close']
        
        # Fibonacci levels
        high_20 = df['high'].rolling(window=20).max()
        low_20 = df['low'].rolling(window=20).min()
        df['fib_23.6'] = high_20 - 0.236 * (high_20 - low_20)
        df['fib_38.2'] = high_20 - 0.382 * (high_20 - low_20)
        df['fib_61.8'] = high_20 - 0.618 * (high_20 - low_20)
        
        # Market structure
        df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
        df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)
        df['inside_bar'] = ((df['high'] < df['high'].shift(1)) & (df['low'] > df['low'].shift(1))).astype(int)
        
        # Time features
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        
        return df.dropna()
    
    def get_enhanced_sentiment_score(self):
        """Get enhanced sentiment analysis from multiple sources"""
        if not self.reddit:
            return 0.0, 0, 0, 0
            
        pos, neg, neu = 0, 0, 0
        total_posts = 0
        
        subreddits = [
            "Bitcoin", "CryptoCurrency", "CryptoMarkets", 
            "Ethereum", "CryptoMoonShots", "BitcoinMarkets"
        ]
        
        try:
            for sub in subreddits:
                for post in self.reddit.subreddit(sub).hot(limit=50):
                    if not post.stickied:
                        # Analyze title and body
                        text = post.title
                        if hasattr(post, 'selftext') and post.selftext:
                            text += " " + post.selftext[:200]  # First 200 chars
                            
                        score = self.analyzer.polarity_scores(text)["compound"]
                        total_posts += 1
                        
                        if score >= 0.1:
                            pos += 1
                        elif score <= -0.1:
                            neg += 1
                        else:
                            neu += 1
                            
        except Exception as e:
            print(f"⚠️ Sentiment analysis error: {e}")
            return 0.0, 10, 10, 20  # Mock data
        
        if total_posts == 0:
            return 0.0, 0, 0, 0
            
        sentiment_score = (pos - neg) / total_posts
        return sentiment_score, pos, neg, neu
    
    def make_enhanced_prediction(self, data, look_back=60):
        """Make prediction using enhanced model"""
        if self.model is None or len(self.feature_names) == 0:
            # Fallback to simple prediction
            current_price = data['close'].iloc[-1]
            return current_price * (1 + np.random.normal(0, 0.02))
        
        try:
            # Engineer features
            enhanced_data = self.engineer_features(data)
            
            if len(enhanced_data) < look_back:
                return data['close'].iloc[-1] * 1.01
            
            # Get the latest features
            feature_data = enhanced_data[self.feature_names].iloc[-look_back:].values
            price_data = enhanced_data[['close']].iloc[-look_back:].values
            
            # Scale features and prices
            scaled_features = self.feature_scaler.transform(feature_data)
            scaled_prices = self.price_scaler.transform(price_data)
            
            # Prepare sequence
            feature_sequence = scaled_features
            price_sequence = scaled_prices.flatten()
            
            combined_sequence = np.column_stack([feature_sequence,
                                               np.tile(price_sequence.reshape(-1, 1), (1, feature_sequence.shape[1]))])
            
            # Reshape for model
            X = combined_sequence.reshape(1, look_back, -1)
            
            # Make prediction
            prediction = self.model.predict(X, verbose=0)
            predicted_price = self.price_scaler.inverse_transform(prediction)[0][0]
            
            return max(predicted_price, 1000)  # Ensure reasonable price
            
        except Exception as e:
            print(f"⚠️ Prediction error: {e}")
            current_price = data['close'].iloc[-1]
            return current_price * (1 + np.random.normal(0, 0.02))
    
    def calculate_position_size(self, signal_strength, current_price):
        """Calculate optimal position size based on signal strength and risk"""
        base_amount = self.usd_balance * self.max_position_size
        
        # Adjust based on signal strength (0 to 1)
        adjusted_amount = base_amount * signal_strength
        
        # Ensure we have enough balance
        max_affordable = min(adjusted_amount, self.usd_balance * 0.95)
        
        return max_affordable
    
    def analyze_market_conditions(self, data):
        """Analyze current market conditions for enhanced decision making"""
        latest = data.iloc[-1]
        
        conditions = {
            'trend': 'neutral',
            'volatility': 'normal',
            'volume': 'normal',
            'momentum': 'neutral'
        }
        
        # Trend analysis
        if 'sma_50' in data.columns and 'sma_100' in data.columns:
            if latest['close'] > latest['sma_50'] > latest['sma_100']:
                conditions['trend'] = 'bullish'
            elif latest['close'] < latest['sma_50'] < latest['sma_100']:
                conditions['trend'] = 'bearish'
        
        # Volatility analysis
        if 'atr' in data.columns:
            recent_atr = data['atr'].tail(20).mean()
            if recent_atr > data['atr'].quantile(0.8):
                conditions['volatility'] = 'high'
            elif recent_atr < data['atr'].quantile(0.2):
                conditions['volatility'] = 'low'
        
        # Volume analysis
        if 'volume_ratio' in data.columns:
            if latest['volume_ratio'] > 1.5:
                conditions['volume'] = 'high'
            elif latest['volume_ratio'] < 0.5:
                conditions['volume'] = 'low'
        
        # Momentum analysis
        if 'rsi_14' in data.columns:
            rsi = latest['rsi_14']
            if rsi > 70:
                conditions['momentum'] = 'overbought'
            elif rsi < 30:
                conditions['momentum'] = 'oversold'
        
        return conditions
    
    def make_enhanced_trading_decision(self):
        """Make trading decision using enhanced analysis"""
        print("🔍 Running enhanced trading analysis...")
        
        # Get data and sentiment
        bitcoin_data = self.get_enhanced_bitcoin_data(90)
        sentiment_score, pos, neg, neu = self.get_enhanced_sentiment_score()
        
        # Get current price and prediction
        current_price = bitcoin_data['close'].iloc[-1]
        predicted_price = self.make_enhanced_prediction(bitcoin_data)
        
        # Analyze market conditions
        market_conditions = self.analyze_market_conditions(bitcoin_data)
        
        # Calculate signals
        signals = {
            'sentiment': 0,
            'technical': 0,
            'prediction': 0,
            'market_structure': 0
        }
        
        # Sentiment signal
        if sentiment_score > 0.2:
            signals['sentiment'] = 1
        elif sentiment_score < -0.2:
            signals['sentiment'] = -1
        
        # Technical signals
        enhanced_data = self.engineer_features(bitcoin_data)
        latest = enhanced_data.iloc[-1]
        
        technical_score = 0
        if 'rsi_14' in enhanced_data.columns:
            rsi = latest['rsi_14']
            if rsi < 30:
                technical_score += 1
            elif rsi > 70:
                technical_score -= 1
        
        if 'bb_position' in enhanced_data.columns:
            bb_pos = latest['bb_position']
            if bb_pos < 0.2:
                technical_score += 1
            elif bb_pos > 0.8:
                technical_score -= 1
        
        signals['technical'] = np.clip(technical_score, -1, 1)
        
        # Prediction signal
        price_change_expected = (predicted_price - current_price) / current_price
        if price_change_expected > 0.02:
            signals['prediction'] = 1
        elif price_change_expected < -0.02:
            signals['prediction'] = -1
        
        # Market structure signal
        if market_conditions['trend'] == 'bullish' and market_conditions['momentum'] != 'overbought':
            signals['market_structure'] = 1
        elif market_conditions['trend'] == 'bearish' and market_conditions['momentum'] != 'oversold':
            signals['market_structure'] = -1
        
        # Combine signals
        total_signal = sum(signals.values())
        signal_strength = abs(total_signal) / 4  # Normalize to 0-1
        
        # Make decision
        action = "HOLD"
        confidence = signal_strength
        
        if total_signal >= 2:  # Strong buy signal
            if self.usd_balance >= 50:
                position_size = self.calculate_position_size(signal_strength, current_price)
                if position_size >= 50:
                    action = "BUY"
                    
        elif total_signal <= -2:  # Strong sell signal
            if self.btc_balance >= 0.001:
                action = "SELL"
        
        # Risk management overrides
        if self.btc_balance > 0:
            # Stop loss
            if current_price <= self.average_buy_price * (1 - self.stop_loss_pct):
                action = "STOP_LOSS"
                confidence = 1.0
            # Take profit
            elif current_price >= self.average_buy_price * (1 + self.take_profit_pct):
                action = "TAKE_PROFIT"
                confidence = 1.0
        
        return {
            'action': action,
            'confidence': confidence,
            'current_price': current_price,
            'predicted_price': predicted_price,
            'sentiment_score': sentiment_score,
            'signals': signals,
            'market_conditions': market_conditions,
            'total_signal': total_signal
        }
    
    def execute_trade(self, decision):
        """Execute the trading decision"""
        action = decision['action']
        current_price = decision['current_price']
        confidence = decision['confidence']
        
        if action == "BUY":
            position_size = self.calculate_position_size(confidence, current_price)
            btc_amount = position_size / current_price
            
            self.usd_balance -= position_size
            old_total = self.btc_balance * self.average_buy_price
            self.btc_balance += btc_amount
            self.average_buy_price = (old_total + position_size) / self.btc_balance
            
            print(f"💰 BUY: {btc_amount:.6f} BTC at ${current_price:,.2f} (${position_size:.2f})")
            
        elif action in ["SELL", "STOP_LOSS", "TAKE_PROFIT"]:
            sell_amount = min(0.001, self.btc_balance)
            usd_gained = sell_amount * current_price
            
            self.btc_balance -= sell_amount
            self.usd_balance += usd_gained
            
            if self.btc_balance == 0:
                self.average_buy_price = 0
                
            print(f"💸 {action}: {sell_amount:.6f} BTC at ${current_price:,.2f} (${usd_gained:.2f})")
        
        # Log trade
        with open("enhanced_trading_log.txt", "a") as f:
            f.write(f"{datetime.now()} | {action} | Price: ${current_price:.2f} | "
                   f"Confidence: {confidence:.2f} | USD: ${self.usd_balance:.2f} | "
                   f"BTC: {self.btc_balance:.6f} | Signals: {decision['signals']}\n")
    
    def run_enhanced_trading_cycle(self):
        """Run one complete enhanced trading cycle"""
        print("\n🚀 Enhanced Trading Bot Cycle Starting...")
        print("=" * 60)
        
        try:
            # Make trading decision
            decision = self.make_enhanced_trading_decision()
            
            # Execute trade
            self.execute_trade(decision)
            
            # Print summary
            print(f"\n📊 Enhanced Analysis Summary:")
            print(f"   Action: {decision['action']}")
            print(f"   Confidence: {decision['confidence']:.2f}")
            print(f"   Current Price: ${decision['current_price']:,.2f}")
            print(f"   Predicted Price: ${decision['predicted_price']:,.2f}")
            print(f"   Sentiment: {decision['sentiment_score']:.4f}")
            print(f"   Signals: {decision['signals']}")
            print(f"   Market: {decision['market_conditions']}")
            print(f"   Portfolio: ${self.usd_balance:.2f} USD + {self.btc_balance:.6f} BTC")
            print("=" * 60)
            
            return decision
            
        except Exception as e:
            print(f"❌ Enhanced trading cycle error: {e}")
            return {'action': 'ERROR', 'error': str(e)}

if __name__ == "__main__":
    bot = EnhancedTradingBot()
    result = bot.run_enhanced_trading_cycle()
    print("Enhanced trading cycle completed!")
