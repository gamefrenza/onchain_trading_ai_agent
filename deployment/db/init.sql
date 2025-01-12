CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(66) UNIQUE,
    symbol VARCHAR(20) NOT NULL,
    amount DECIMAL NOT NULL,
    price DECIMAL NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    type VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    prediction DECIMAL NOT NULL,
    confidence DECIMAL NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    total_return DECIMAL NOT NULL,
    sharpe_ratio DECIMAL NOT NULL,
    max_drawdown DECIMAL NOT NULL,
    win_rate DECIMAL NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_predictions_symbol_timestamp ON predictions(symbol, timestamp); 