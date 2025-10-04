# AI-Powered Crypto Trading System
# AI-Powered Crypto Trading System

An advanced cryptocurrency trading system that combines on-chain data analysis, technical indicators, machine learning, and automated trading execution with a real-time web dashboard.

## Features

### 1. On-Chain Data Analysis
- Real-time data fetching from Ethereum blockchain
- Uniswap V2 swap event monitoring
- Price and volume data aggregation
- Configurable block range analysis

### 2. Technical Analysis
- Multiple technical indicators:
  - Simple and Exponential Moving Averages (7 and 21 periods)
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
  - Bollinger Bands
- Customizable indicator parameters
- Real-time indicator calculations

### 3. Machine Learning Integration
- Automated trading signal generation
- Feature engineering from technical indicators
- Support for multiple ML models:
  - Logistic Regression
  - Support Vector Machine
- Configurable confidence thresholds
- Model performance evaluation metrics

### 4. Risk Management
- Configurable stop-loss and take-profit levels
- Position size management
- Slippage protection
- Maximum position limits
- Trading interval controls

### 5. Interactive Dashboard
- Real-time price charts
- Technical indicator visualizations
- Current position monitoring
- P&L tracking
- Manual trading controls
- Auto-refresh functionality

### 6. Smart Contract Integration
- Secure transaction execution
- Gas optimization
- Transaction receipt verification
- Error handling and logging

## Setup Instructions

1. Install Dependencies
```bash
pip install -r requirements.txt
```

2. Install TA-Lib (Technical Analysis Library)
- Windows: Download and install wheel file from unofficial binaries
- Linux: `sudo apt-get install ta-lib`
- macOS: `brew install ta-lib`

3. Configure Environment
- Create a `.env` file with required parameters:
```
ETHEREUM_NODE_URL=your_ethereum_node_url
TRADING_CONTRACT_ADDRESS=your_contract_address
TRADER_PRIVATE_KEY=your_private_key_hex
```
- Never commit secrets. Use secure key management in production.

4. Update Configuration
- Modify `trading_config.json` with your desired parameters:
  - Risk management settings
  - Trading intervals
  - Analysis parameters
  - Token addresses

## Usage

### Starting the Dashboard
```bash
streamlit run trading_dashboard.py
```

### Dashboard Features

1. **Market Data View**
- Real-time price charts with candlesticks
- Volume analysis
- Technical indicator overlays
- Recent trades table

2. **Trading Controls**
- Manual buy/sell buttons
- Position size input
- Slippage tolerance adjustment
- Trade confirmation dialog

3. **Performance Metrics**
- Current position status
- P&L tracking
- Last trade information
- Portfolio analytics

4. **Settings**
- Auto-refresh toggle
- Refresh interval adjustment
- Trading parameters configuration

### Running the Trading Agent
```bash
python trading_agent.py
```

## Project Structure

```
GEMINI_VERSION/
├── trading_dashboard.py    # Streamlit web interface
├── trading_agent.py        # Main trading logic
├── technical_indicators.py # Technical analysis (TA-Lib)
├── contract_trader.py      # Smart contract interaction
├── uniswap_data_fetcher.py # On-chain data → OHLCV aggregation
├── ml_trading_signals.py   # ML signal generation
├── trading_config.json     # Configuration file
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

## Security Considerations

1. **Private Key Management**
- Never store private keys in code or environment variables
- Use secure key management solutions:
  - Hardware wallets
  - Key management services (AWS KMS, Azure Key Vault)
  - Secure encrypted storage

2. **Transaction Safety**
- Always use slippage protection
- Implement gas price limits
- Verify transaction receipts
- Monitor for failed transactions

3. **Risk Management**
- Start with small position sizes
- Test thoroughly on testnet first
- Monitor system performance
- Implement emergency stop functionality

## Development Guidelines

1. **Testing**
- Run extensive backtests before live trading
- Test all components individually
- Verify risk management rules
- Simulate various market conditions

2. **Monitoring**
- Check logs regularly
- Monitor system resource usage
- Track trading performance
- Set up alerts for critical events

3. **Maintenance**
- Regularly update dependencies
- Monitor gas prices and network conditions
- Backup configuration and data
- Update ML models periodically

## Troubleshooting

- Web3 connection failed: Ensure `ETHEREUM_NODE_URL` is valid and reachable.
- Missing private key: Set `TRADER_PRIVATE_KEY` in `.env` for signing.
- TA-Lib install errors: Install OS-level TA-Lib first, then the Python package.
- No chart data: The app aggregates Uniswap V2 WETH/USDC swaps into OHLCV; wait for recent blocks or reduce `blocks_to_analyze` in `trading_config.json`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This trading system is for educational purposes only. Cryptocurrency trading involves significant risk of loss. Use this system at your own risk and always perform thorough testing before deploying with real funds.

## Support

For issues, questions, or contributions, please open an issue in the repository.

---

Remember to always:
- Test thoroughly on testnet first
- Start with small positions
- Monitor system performance
- Keep private keys secure
- Stay updated with market conditions

