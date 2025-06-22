
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json

class BacktestEngine:
    def __init__(self, initial_balance=1000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.btc_holdings = 0
        self.trades = []
        self.portfolio_values = []
        
    def get_historical_data(self, days=30):
        """Get historical BTC data for backtesting"""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {"vs_currency": "usd", "days": days, "interval": "daily"}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Convert to DataFrame
            prices_df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            prices_df['date'] = pd.to_datetime(prices_df['timestamp'], unit='ms')
            prices_df = prices_df.set_index('date')
            
            return prices_df
            
        except Exception as e:
            print(f"⚠️ Using mock historical data: {e}")
            # Create mock data for testing
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            base_price = 65000
            prices = []
            for i in range(days):
                daily_change = np.random.normal(0, 0.03)  # 3% daily volatility
                price = base_price * (1 + daily_change)
                prices.append(price)
                base_price = price
            
            return pd.DataFrame({'price': prices}, index=dates)
    
    def simulate_sentiment(self, price_change):
        """Simulate sentiment based on price movements"""
        # Simple model: positive sentiment follows price increases
        base_sentiment = np.random.normal(0, 0.2)
        trend_sentiment = price_change * 0.5  # Sentiment follows price trends
        return np.clip(base_sentiment + trend_sentiment, -1, 1)
    
    def backtest_strategy(self, days=30):
        """Run backtest of trading strategy"""
        print(f"🔄 Running {days}-day backtest...")
        
        # Get historical data
        price_data = self.get_historical_data(days)
        
        for i in range(1, len(price_data)):
            current_price = price_data.iloc[i]['price']
            previous_price = price_data.iloc[i-1]['price']
            price_change = (current_price - previous_price) / previous_price
            
            # Simulate sentiment
            sentiment = self.simulate_sentiment(price_change)
            
            # Trading decision logic (simplified version of your bot)
            action = "HOLD"
            
            if sentiment > 0.3 and self.balance >= 100:
                # Buy signal
                buy_amount = min(100, self.balance)
                btc_bought = buy_amount / current_price
                self.balance -= buy_amount
                self.btc_holdings += btc_bought
                action = "BUY"
                
                self.trades.append({
                    'date': price_data.index[i],
                    'action': action,
                    'price': current_price,
                    'amount': btc_bought,
                    'sentiment': sentiment,
                    'balance': self.balance,
                    'btc_holdings': self.btc_holdings
                })
                
            elif sentiment < -0.3 and self.btc_holdings > 0.001:
                # Sell signal
                btc_to_sell = min(0.001, self.btc_holdings)
                sell_value = btc_to_sell * current_price
                self.balance += sell_value
                self.btc_holdings -= btc_to_sell
                action = "SELL"
                
                self.trades.append({
                    'date': price_data.index[i],
                    'action': action,
                    'price': current_price,
                    'amount': btc_to_sell,
                    'sentiment': sentiment,
                    'balance': self.balance,
                    'btc_holdings': self.btc_holdings
                })
            
            # Calculate portfolio value
            portfolio_value = self.balance + (self.btc_holdings * current_price)
            self.portfolio_values.append({
                'date': price_data.index[i],
                'value': portfolio_value,
                'price': current_price,
                'sentiment': sentiment
            })
        
        self.analyze_results()
        
    def analyze_results(self):
        """Analyze backtest results"""
        if not self.portfolio_values:
            print("❌ No backtest data to analyze")
            return
            
        final_value = self.portfolio_values[-1]['value']
        total_return = ((final_value - self.initial_balance) / self.initial_balance) * 100
        
        # Calculate buy and hold return
        initial_price = self.portfolio_values[0]['price']
        final_price = self.portfolio_values[-1]['price']
        buy_hold_return = ((final_price - initial_price) / initial_price) * 100
        
        print(f"\n📊 Backtest Results:")
        print(f"   Initial Balance: ${self.initial_balance:,.2f}")
        print(f"   Final Portfolio Value: ${final_value:,.2f}")
        print(f"   Total Return: {total_return:+.2f}%")
        print(f"   Buy & Hold Return: {buy_hold_return:+.2f}%")
        print(f"   Strategy vs Buy & Hold: {total_return - buy_hold_return:+.2f}%")
        print(f"   Total Trades: {len(self.trades)}")
        
        # Count trade types
        buy_trades = len([t for t in self.trades if t['action'] == 'BUY'])
        sell_trades = len([t for t in self.trades if t['action'] == 'SELL'])
        print(f"   Buy Trades: {buy_trades}")
        print(f"   Sell Trades: {sell_trades}")
        
        # Create visualization
        self.create_backtest_chart()
        
        # Save results
        with open('backtest_results.json', 'w') as f:
            json.dump({
                'portfolio_values': [(pv['date'].isoformat(), pv['value'], pv['price']) for pv in self.portfolio_values],
                'trades': [(t['date'].isoformat(), t['action'], t['price'], t['sentiment']) for t in self.trades],
                'summary': {
                    'initial_balance': self.initial_balance,
                    'final_value': final_value,
                    'total_return': total_return,
                    'buy_hold_return': buy_hold_return,
                    'total_trades': len(self.trades)
                }
            }, f, indent=2)
        
        print("💾 Results saved to 'backtest_results.json'")
    
    def create_backtest_chart(self):
        """Create visualization of backtest results"""
        if not self.portfolio_values:
            return
            
        dates = [pv['date'] for pv in self.portfolio_values]
        portfolio_values = [pv['value'] for pv in self.portfolio_values]
        btc_prices = [pv['price'] for pv in self.portfolio_values]
        sentiments = [pv['sentiment'] for pv in self.portfolio_values]
        
        # Normalize BTC prices for comparison
        initial_btc_price = btc_prices[0]
        normalized_btc = [(price / initial_btc_price) * self.initial_balance for price in btc_prices]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Portfolio performance
        ax1.plot(dates, portfolio_values, 'g-', linewidth=2, label='Bot Strategy')
        ax1.plot(dates, normalized_btc, 'b--', linewidth=2, label='Buy & Hold')
        ax1.set_ylabel('Portfolio Value (USD)')
        ax1.set_title('Trading Bot Backtest Results')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Mark trades
        for trade in self.trades:
            if trade['action'] == 'BUY':
                ax1.scatter(trade['date'], self.balance + (self.btc_holdings * trade['price']), 
                           color='green', marker='^', s=50, alpha=0.7)
            else:
                ax1.scatter(trade['date'], self.balance + (self.btc_holdings * trade['price']), 
                           color='red', marker='v', s=50, alpha=0.7)
        
        # Sentiment over time
        ax2.plot(dates, sentiments, 'r-', linewidth=1, alpha=0.7, label='Sentiment')
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax2.axhline(y=0.3, color='green', linestyle=':', alpha=0.5, label='Buy Threshold')
        ax2.axhline(y=-0.3, color='red', linestyle=':', alpha=0.5, label='Sell Threshold')
        ax2.set_ylabel('Sentiment Score')
        ax2.set_xlabel('Date')
        ax2.set_title('Sentiment Analysis Over Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('backtest_visualization.png', dpi=300, bbox_inches='tight')
        print("📈 Backtest chart saved as 'backtest_visualization.png'")

if __name__ == "__main__":
    # Run 30-day backtest
    engine = BacktestEngine(initial_balance=1000)
    engine.backtest_strategy(days=30)
