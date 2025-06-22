
import requests
import time
import json
from datetime import datetime, timedelta
from trading_bot import get_sentiment_score, predict_next_day_price, get_real_btc_price
import matplotlib.pyplot as plt

class BotValidator:
    def __init__(self):
        self.predictions = []
        self.actual_prices = []
        self.sentiment_scores = []
        
    def record_prediction(self):
        """Record a prediction and current price"""
        try:
            sentiment_score, pos, neg, neu = get_sentiment_score()
            current_price = get_real_btc_price()
            
            # Store prediction data
            prediction_data = {
                'timestamp': datetime.now().isoformat(),
                'sentiment_score': sentiment_score,
                'current_price': current_price,
                'positive_posts': pos,
                'negative_posts': neg,
                'neutral_posts': neu
            }
            
            # Save to file for tracking
            with open('prediction_log.json', 'a') as f:
                f.write(json.dumps(prediction_data) + '\n')
                
            print(f"✅ Recorded: Price ${current_price:,.2f}, Sentiment {sentiment_score:.4f}")
            return prediction_data
            
        except Exception as e:
            print(f"❌ Error recording prediction: {e}")
            return None
    
    def validate_predictions(self):
        """Validate past predictions against actual prices"""
        try:
            predictions = []
            with open('prediction_log.json', 'r') as f:
                for line in f:
                    predictions.append(json.loads(line.strip()))
            
            if len(predictions) < 2:
                print("⚠️ Need at least 2 predictions to validate")
                return
            
            # Calculate accuracy metrics
            correct_direction = 0
            total_predictions = 0
            
            for i in range(len(predictions) - 1):
                current = predictions[i]
                future = predictions[i + 1]
                
                # Check if sentiment predicted price direction correctly
                sentiment = current['sentiment_score']
                price_change = (future['current_price'] - current['current_price']) / current['current_price']
                
                if (sentiment > 0 and price_change > 0) or (sentiment < 0 and price_change < 0):
                    correct_direction += 1
                total_predictions += 1
            
            accuracy = (correct_direction / total_predictions) * 100 if total_predictions > 0 else 0
            
            print(f"📊 Bot Accuracy Report:")
            print(f"   Direction Accuracy: {accuracy:.1f}% ({correct_direction}/{total_predictions})")
            print(f"   Total Predictions: {len(predictions)}")
            
            # Create visualization
            self.create_accuracy_chart(predictions)
            
        except FileNotFoundError:
            print("⚠️ No prediction log found. Run record_prediction() first.")
        except Exception as e:
            print(f"❌ Error validating: {e}")
    
    def create_accuracy_chart(self, predictions):
        """Create visual chart of predictions vs reality"""
        if len(predictions) < 2:
            return
            
        times = [datetime.fromisoformat(p['timestamp']) for p in predictions]
        prices = [p['current_price'] for p in predictions]
        sentiments = [p['sentiment_score'] for p in predictions]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Price chart
        ax1.plot(times, prices, 'b-', linewidth=2, label='Actual BTC Price')
        ax1.set_ylabel('Price (USD)')
        ax1.set_title('BTC Price Tracking')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Sentiment chart
        ax2.plot(times, sentiments, 'r-', linewidth=2, label='Sentiment Score')
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax2.set_ylabel('Sentiment Score')
        ax2.set_xlabel('Time')
        ax2.set_title('Sentiment Analysis')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('bot_validation_report.png', dpi=300, bbox_inches='tight')
        print("📈 Validation chart saved as 'bot_validation_report.png'")

if __name__ == "__main__":
    validator = BotValidator()
    
    # Record current prediction
    validator.record_prediction()
    
    # Validate past predictions
    validator.validate_predictions()
