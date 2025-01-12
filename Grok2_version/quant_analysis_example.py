import pandas as pd
from blockchain_data import BlockchainDataFetcher
from quant_analysis import QuantAnalyzer
import asyncio
from datetime import datetime, timedelta

async def main():
    # Initialize the blockchain data fetcher
    fetcher = BlockchainDataFetcher()
    
    # Fetch historical trading data
    trades = await fetcher.get_dex_trades(pair='ETH/USDT', limit=1000)
    
    # Convert to DataFrame
    df = pd.DataFrame(trades)
    
    # Initialize the quantitative analyzer
    analyzer = QuantAnalyzer(lookback_period=100)
    
    # Prepare and analyze data
    df = analyzer.prepare_data(df)
    df = analyzer.add_technical_indicators(df)
    
    # Train the model
    analyzer.train_model(df)
    
    # Generate trading signals
    signals = analyzer.generate_trading_signals(df)
    
    # Print recent signals
    print("\nRecent Trading Signals:")
    for signal in signals[-5:]:
        print(f"Time: {signal.timestamp}")
        print(f"Type: {signal.signal_type.upper()}")
        print(f"Confidence: {signal.confidence:.2f}")
        print(f"Price: {signal.price:.2f}")
        print("Indicators:", signal.indicators)
        print("---")
    
    # Backtest the strategy
    backtest_results = analyzer.backtest_strategy(df)
    
    print("\nBacktest Results:")
    print(f"Initial Capital: ${backtest_results['initial_capital']:.2f}")
    print(f"Final Value: ${backtest_results['final_value']:.2f}")
    print(f"ROI: {backtest_results['roi_percent']:.2f}%")
    print(f"Number of Trades: {backtest_results['num_trades']}")

if __name__ == "__main__":
    asyncio.run(main()) 