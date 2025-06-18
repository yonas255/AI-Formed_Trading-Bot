CREATE TABLE trades (
    trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('BUY', 'SELL', 'HOLD', 'STOP-LOSS', 'TAKE-PROFIT')),
    sentiment_score REAL NOT NULL,
    predicted_btc_price REAL NOT NULL,
    actual_btc_price REAL NOT NULL,
    usd_balance REAL NOT NULL,
    btc_balance REAL NOT NULL
);
