
#!/usr/bin/env python3
"""
Simple script to train a fresh Bitcoin prediction model
"""

print("🚀 Starting Bitcoin Model Training...")
print("This will take 5-10 minutes depending on your internet speed and data size.")
print("=" * 60)

try:
    from train_model import BitcoinModelTrainer
    
    # Initialize trainer with good parameters
    trainer = BitcoinModelTrainer(
        days_of_data=180,  # 6 months of data for good training
        look_back=60       # 60-day lookback window
    )
    
    # Run the full training pipeline
    metrics = trainer.run_full_training()
    
    print("\n🎉 SUCCESS!")
    print("Your trading bot now has a fresh, trained model!")
    
except Exception as e:
    print(f"\n❌ Training Error: {e}")
    print("💡 Possible solutions:")
    print("1. Check your internet connection")
    print("2. Try running again (APIs might be temporarily down)")
    print("3. The training script will use mock data if APIs fail")
