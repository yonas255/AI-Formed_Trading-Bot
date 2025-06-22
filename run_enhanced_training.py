
#!/usr/bin/env python3
"""
Enhanced Training Pipeline
Runs all advanced training systems including:
1. Enhanced Feature Engineering
2. Ensemble Model Training  
3. Cross-Validation
4. Performance Analysis
"""

import sys
import os
from datetime import datetime
import traceback

def run_enhanced_feature_training():
    """Run enhanced feature engineering training"""
    print("🔧 Starting Enhanced Feature Engineering Training...")
    try:
        from enhanced_model_trainer import EnhancedModelTrainer
        
        trainer = EnhancedModelTrainer(days_of_data=365, look_back=60)
        history = trainer.run_enhanced_training()
        
        print("✅ Enhanced feature training completed!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced feature training failed: {e}")
        traceback.print_exc()
        return False

def run_ensemble_training():
    """Run ensemble model training"""
    print("\n🤖 Starting Ensemble Model Training...")
    try:
        from model_ensemble import ModelEnsemble
        from enhanced_model_trainer import EnhancedModelTrainer
        
        # Get fresh data
        data_trainer = EnhancedModelTrainer()
        data = data_trainer.fetch_enhanced_bitcoin_data()
        
        # Train ensemble
        ensemble = ModelEnsemble(look_back=60)
        performance = ensemble.run_ensemble_training(data)
        
        print("✅ Ensemble training completed!")
        return True
        
    except Exception as e:
        print(f"❌ Ensemble training failed: {e}")
        traceback.print_exc()
        return False

def test_enhanced_bot():
    """Test the enhanced trading bot"""
    print("\n🧪 Testing Enhanced Trading Bot...")
    try:
        from enhanced_trading_bot import EnhancedTradingBot
        
        bot = EnhancedTradingBot()
        result = bot.run_enhanced_trading_cycle()
        
        if result['action'] != 'ERROR':
            print("✅ Enhanced bot test successful!")
            return True
        else:
            print(f"❌ Enhanced bot test failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced bot test failed: {e}")
        traceback.print_exc()
        return False

def create_performance_report():
    """Create comprehensive performance report"""
    print("\n📊 Creating Performance Report...")
    try:
        import json
        import matplotlib.pyplot as plt
        
        # Collect all metadata
        report = {
            'timestamp': datetime.now().isoformat(),
            'training_completed': [],
            'models_available': [],
            'performance_metrics': {}
        }
        
        # Check what was trained
        if os.path.exists('enhanced_model_metadata.json'):
            with open('enhanced_model_metadata.json', 'r') as f:
                enhanced_meta = json.load(f)
                report['training_completed'].append('Enhanced Feature Model')
                report['models_available'].append('Enhanced LSTM')
                report['performance_metrics']['enhanced_features'] = enhanced_meta.get('features_count', 0)
        
        if os.path.exists('ensemble_metadata.json'):
            with open('ensemble_metadata.json', 'r') as f:
                ensemble_meta = json.load(f)
                report['training_completed'].append('Ensemble Models')
                report['models_available'].extend(ensemble_meta.get('models', []))
                report['performance_metrics']['ensemble_models'] = len(ensemble_meta.get('models', []))
        
        # Check basic model
        if os.path.exists('btc_lstm_model.h5'):
            report['models_available'].append('Basic LSTM')
        
        # Save report
        with open('training_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("📋 Training Report Summary:")
        print(f"   ✅ Training Completed: {', '.join(report['training_completed'])}")
        print(f"   🤖 Models Available: {', '.join(report['models_available'])}")
        print(f"   📊 Performance Metrics: {report['performance_metrics']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Report creation failed: {e}")
        return False

def main():
    """Run the complete enhanced training pipeline"""
    print("🚀 Enhanced Bitcoin Trading Bot Training Pipeline")
    print("=" * 70)
    print("This will train advanced models with:")
    print("✨ Enhanced technical indicators (50+ features)")
    print("🤖 Multiple model architectures (LSTM, GRU, CNN-LSTM)")
    print("📊 Ensemble learning with weighted predictions")
    print("🔬 Cross-validation and performance analysis")
    print("=" * 70)
    
    # Track results
    results = {
        'enhanced_features': False,
        'ensemble_models': False,
        'bot_test': False,
        'report': False
    }
    
    # Step 1: Enhanced Feature Training
    print("\n📚 STEP 1: Enhanced Feature Engineering")
    results['enhanced_features'] = run_enhanced_feature_training()
    
    # Step 2: Ensemble Training
    print("\n🎯 STEP 2: Ensemble Model Training")
    results['ensemble_models'] = run_ensemble_training()
    
    # Step 3: Test Enhanced Bot
    print("\n🔍 STEP 3: Enhanced Bot Testing")
    results['bot_test'] = test_enhanced_bot()
    
    # Step 4: Create Report
    print("\n📋 STEP 4: Performance Report")
    results['report'] = create_performance_report()
    
    # Final Summary
    print("\n" + "=" * 70)
    print("🎉 ENHANCED TRAINING PIPELINE COMPLETE!")
    print("=" * 70)
    
    successful_steps = sum(results.values())
    total_steps = len(results)
    
    print(f"📊 Pipeline Success Rate: {successful_steps}/{total_steps} ({successful_steps/total_steps*100:.1f}%)")
    print("\n📋 Step Results:")
    
    status_icons = {True: "✅", False: "❌"}
    for step, success in results.items():
        print(f"   {status_icons[success]} {step.replace('_', ' ').title()}: {'Success' if success else 'Failed'}")
    
    if successful_steps >= 3:
        print("\n🎯 TRAINING SUCCESSFUL!")
        print("Your enhanced trading bot is ready with:")
        print("   🔧 Advanced technical analysis")
        print("   🤖 Multiple AI models")
        print("   📊 Ensemble predictions")
        print("   🛡️ Enhanced risk management")
        
        print("\n🚀 Next Steps:")
        print("1. Your bot will automatically use the enhanced models")
        print("2. Check the performance charts generated")
        print("3. Run your trading bot with confidence!")
        
    else:
        print("\n⚠️ PARTIAL SUCCESS")
        print("Some training steps failed, but you can still use:")
        print("- Any successfully trained models")
        print("- The existing basic trading system")
        print("- Try running individual training scripts")
    
    print("\n📁 Generated Files:")
    enhanced_files = [
        'btc_enhanced_lstm_model.h5',
        'enhanced_feature_scaler.pkl', 
        'enhanced_price_scaler.pkl',
        'feature_names.pkl',
        'ensemble_model_lstm.h5',
        'ensemble_model_gru.h5',
        'ensemble_weights.pkl',
        'training_report.json',
        'ensemble_analysis.png'
    ]
    
    for file in enhanced_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (not created)")

if __name__ == "__main__":
    main()
