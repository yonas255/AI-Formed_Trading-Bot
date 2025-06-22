
import numpy as np
import pandas as pd
import pickle
from datetime import datetime
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU, Conv1D, MaxPooling1D, Flatten
    from tensorflow.keras.optimizers import Adam, RMSprop
except ImportError:
    print("Installing TensorFlow...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'tensorflow'])
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU, Conv1D, MaxPooling1D, Flatten
    from tensorflow.keras.optimizers import Adam, RMSprop

class ModelEnsemble:
    def __init__(self, look_back=60):
        self.look_back = look_back
        self.models = {}
        self.weights = {}
        self.scalers = {}
        self.performance_history = {}
        
    def create_lstm_model(self, input_shape, name="LSTM"):
        """Create LSTM model"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        return model
    
    def create_gru_model(self, input_shape, name="GRU"):
        """Create GRU model"""
        model = Sequential([
            GRU(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            GRU(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        model.compile(optimizer=RMSprop(learning_rate=0.001), loss='mse', metrics=['mae'])
        return model
    
    def create_cnn_lstm_model(self, input_shape, name="CNN_LSTM"):
        """Create CNN-LSTM hybrid model"""
        model = Sequential([
            Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=input_shape),
            Conv1D(filters=32, kernel_size=3, activation='relu'),
            MaxPooling1D(pool_size=2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        return model
    
    def create_deep_lstm_model(self, input_shape, name="Deep_LSTM"):
        """Create deep LSTM model"""
        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=input_shape),
            Dropout(0.3),
            LSTM(100, return_sequences=True),
            Dropout(0.3),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(50),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.0005), loss='huber', metrics=['mae'])
        return model
    
    def prepare_data_for_ensemble(self, data):
        """Prepare data for ensemble training"""
        from sklearn.preprocessing import MinMaxScaler
        
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data[['close']])
        
        X, y = [], []
        for i in range(self.look_back, len(scaled_data)):
            X.append(scaled_data[i-self.look_back:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y, scaler
    
    def cross_validate_model(self, model_func, X, y, n_splits=5):
        """Perform time series cross-validation"""
        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_scores = []
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            print(f"  Fold {fold + 1}/{n_splits}")
            
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Create and train model
            model = model_func(input_shape=(X.shape[1], X.shape[2]))
            
            model.fit(
                X_train, y_train,
                epochs=50,
                batch_size=32,
                validation_data=(X_val, y_val),
                verbose=0
            )
            
            # Evaluate
            y_pred = model.predict(X_val, verbose=0)
            mse = mean_squared_error(y_val, y_pred)
            cv_scores.append(mse)
        
        return np.mean(cv_scores), np.std(cv_scores)
    
    def train_ensemble_models(self, data):
        """Train multiple models for ensemble"""
        print("🔄 Training ensemble models...")
        
        # Prepare data
        X, y, scaler = self.prepare_data_for_ensemble(data)
        self.scalers['ensemble_scaler'] = scaler
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Define models to train
        model_configs = [
            ("LSTM", self.create_lstm_model),
            ("GRU", self.create_gru_model),
            ("CNN_LSTM", self.create_cnn_lstm_model),
            ("Deep_LSTM", self.create_deep_lstm_model)
        ]
        
        model_performance = {}
        
        for name, model_func in model_configs:
            print(f"\n🔧 Training {name} model...")
            
            # Cross-validation
            cv_mean, cv_std = self.cross_validate_model(model_func, X_train, y_train)
            print(f"   CV Score: {cv_mean:.6f} ± {cv_std:.6f}")
            
            # Train final model on full training set
            model = model_func(input_shape=(X.shape[1], X.shape[2]))
            
            history = model.fit(
                X_train, y_train,
                epochs=100,
                batch_size=32,
                validation_data=(X_test, y_test),
                verbose=0
            )
            
            # Evaluate on test set
            y_pred = model.predict(X_test, verbose=0)
            test_mse = mean_squared_error(y_test, y_pred)
            test_mae = mean_absolute_error(y_test, y_pred)
            
            # Store model and performance
            self.models[name] = model
            model_performance[name] = {
                'cv_mean': cv_mean,
                'cv_std': cv_std,
                'test_mse': test_mse,
                'test_mae': test_mae,
                'final_val_loss': history.history['val_loss'][-1]
            }
            
            print(f"   Test MSE: {test_mse:.6f}")
            print(f"   Test MAE: {test_mae:.6f}")
        
        # Calculate ensemble weights based on performance
        self.calculate_ensemble_weights(model_performance)
        
        # Save models
        self.save_ensemble_models()
        
        return model_performance
    
    def calculate_ensemble_weights(self, performance):
        """Calculate weights for ensemble based on performance"""
        print("\n📊 Calculating ensemble weights...")
        
        # Use inverse of test MSE as weights (better performance = higher weight)
        mse_scores = {name: perf['test_mse'] for name, perf in performance.items()}
        
        # Invert MSE scores (lower MSE = higher weight)
        inverse_scores = {name: 1.0 / mse for name, mse in mse_scores.items()}
        
        # Normalize to sum to 1
        total_score = sum(inverse_scores.values())
        self.weights = {name: score / total_score for name, score in inverse_scores.items()}
        
        print("   Model weights:")
        for name, weight in self.weights.items():
            print(f"     {name}: {weight:.3f}")
    
    def make_ensemble_prediction(self, data):
        """Make prediction using ensemble of models"""
        if not self.models or not self.weights:
            print("⚠️ Ensemble not trained")
            return None
        
        try:
            # Prepare input data
            scaler = self.scalers['ensemble_scaler']
            scaled_data = scaler.transform(data[['close']].tail(self.look_back))
            X = scaled_data.reshape(1, self.look_back, 1)
            
            # Get predictions from each model
            predictions = {}
            for name, model in self.models.items():
                pred = model.predict(X, verbose=0)[0][0]
                predictions[name] = pred
            
            # Calculate weighted ensemble prediction
            ensemble_pred = sum(pred * self.weights[name] for name, pred in predictions.items())
            
            # Inverse transform to get actual price
            ensemble_pred = scaler.inverse_transform([[ensemble_pred]])[0][0]
            
            return {
                'ensemble_prediction': ensemble_pred,
                'individual_predictions': {name: scaler.inverse_transform([[pred]])[0][0] 
                                         for name, pred in predictions.items()},
                'weights': self.weights
            }
            
        except Exception as e:
            print(f"❌ Ensemble prediction error: {e}")
            return None
    
    def save_ensemble_models(self):
        """Save all ensemble models and metadata"""
        print("💾 Saving ensemble models...")
        
        # Save individual models
        for name, model in self.models.items():
            model.save(f'ensemble_model_{name.lower()}.h5')
        
        # Save weights and scalers
        with open('ensemble_weights.pkl', 'wb') as f:
            pickle.dump(self.weights, f)
        
        with open('ensemble_scalers.pkl', 'wb') as f:
            pickle.dump(self.scalers, f)
        
        # Save metadata
        metadata = {
            'creation_date': datetime.now().isoformat(),
            'look_back': self.look_back,
            'models': list(self.models.keys()),
            'weights': self.weights,
            'performance': self.performance_history
        }
        
        with open('ensemble_metadata.json', 'w') as f:
            import json
            json.dump(metadata, f, indent=2)
        
        print("✅ Ensemble models saved")
    
    def load_ensemble_models(self):
        """Load ensemble models and metadata"""
        try:
            # Load models
            import os
            model_files = [f for f in os.listdir('.') if f.startswith('ensemble_model_') and f.endswith('.h5')]
            
            for file in model_files:
                name = file.replace('ensemble_model_', '').replace('.h5', '').upper()
                self.models[name] = load_model(file)
            
            # Load weights and scalers
            if os.path.exists('ensemble_weights.pkl'):
                with open('ensemble_weights.pkl', 'rb') as f:
                    self.weights = pickle.load(f)
            
            if os.path.exists('ensemble_scalers.pkl'):
                with open('ensemble_scalers.pkl', 'rb') as f:
                    self.scalers = pickle.load(f)
            
            print(f"✅ Loaded {len(self.models)} ensemble models")
            return True
            
        except Exception as e:
            print(f"❌ Error loading ensemble: {e}")
            return False
    
    def create_ensemble_visualization(self, data, predictions=None):
        """Create visualization of ensemble performance"""
        if predictions is None:
            predictions = self.make_ensemble_prediction(data)
        
        if predictions is None:
            return
        
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Recent price history
        plt.subplot(2, 2, 1)
        recent_data = data.tail(60)
        plt.plot(recent_data.index, recent_data['close'], 'b-', linewidth=2, label='Actual Price')
        plt.title('Recent Price History (60 days)')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Individual model predictions
        plt.subplot(2, 2, 2)
        models = list(predictions['individual_predictions'].keys())
        pred_values = list(predictions['individual_predictions'].values())
        colors = ['red', 'green', 'orange', 'purple']
        
        bars = plt.bar(models, pred_values, color=colors[:len(models)], alpha=0.7)
        plt.axhline(y=predictions['ensemble_prediction'], color='black', linestyle='--', 
                   linewidth=2, label=f'Ensemble: ${predictions["ensemble_prediction"]:,.2f}')
        
        plt.title('Model Predictions Comparison')
        plt.ylabel('Predicted Price (USD)')
        plt.legend()
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, pred_values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.01,
                    f'${value:,.0f}', ha='center', va='bottom')
        
        # Plot 3: Model weights
        plt.subplot(2, 2, 3)
        weights = list(predictions['weights'].values())
        plt.pie(weights, labels=models, autopct='%1.1f%%', startangle=90)
        plt.title('Ensemble Model Weights')
        
        # Plot 4: Prediction confidence
        plt.subplot(2, 2, 4)
        current_price = data['close'].iloc[-1]
        price_changes = [(pred - current_price) / current_price * 100 
                        for pred in pred_values]
        ensemble_change = (predictions['ensemble_prediction'] - current_price) / current_price * 100
        
        bars = plt.bar(models + ['Ensemble'], price_changes + [ensemble_change], 
                      color=colors[:len(models)] + ['black'], alpha=0.7)
        plt.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        plt.title('Predicted Price Changes (%)')
        plt.ylabel('Change from Current Price (%)')
        plt.xticks(rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, price_changes + [ensemble_change]):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.1 if value >= 0 else bar.get_height() - abs(value)*0.1,
                    f'{value:+.1f}%', ha='center', va='bottom' if value >= 0 else 'top')
        
        plt.tight_layout()
        plt.savefig('ensemble_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("📈 Ensemble analysis chart saved as 'ensemble_analysis.png'")
    
    def run_ensemble_training(self, data):
        """Run complete ensemble training pipeline"""
        print("🎯 Starting Ensemble Model Training")
        print("=" * 60)
        
        # Train ensemble
        performance = self.train_ensemble_models(data)
        
        # Create visualization
        self.create_ensemble_visualization(data)
        
        print("\n🎉 Ensemble training completed!")
        print(f"📊 Trained {len(self.models)} models:")
        for name, perf in performance.items():
            print(f"   {name}: MSE={perf['test_mse']:.6f}, Weight={self.weights[name]:.3f}")
        
        return performance

class EnsemblePredictor:
    """Simple class to use trained ensemble for predictions"""
    
    def __init__(self):
        self.ensemble = ModelEnsemble()
        self.load_ensemble()
    
    def load_ensemble(self):
        """Load trained ensemble"""
        success = self.ensemble.load_ensemble_models()
        if success:
            print("✅ Ensemble loaded successfully")
        else:
            print("⚠️ No trained ensemble found")
    
    def predict(self, data):
        """Make prediction using ensemble"""
        return self.ensemble.make_ensemble_prediction(data)

if __name__ == "__main__":
    # Example usage
    from enhanced_model_trainer import EnhancedModelTrainer
    
    # Get data
    trainer = EnhancedModelTrainer()
    data = trainer.fetch_enhanced_bitcoin_data()
    
    # Train ensemble
    ensemble = ModelEnsemble()
    ensemble.run_ensemble_training(data)
    
    # Make prediction
    prediction = ensemble.make_ensemble_prediction(data)
    if prediction:
        print(f"\n🔮 Ensemble Prediction: ${prediction['ensemble_prediction']:,.2f}")
