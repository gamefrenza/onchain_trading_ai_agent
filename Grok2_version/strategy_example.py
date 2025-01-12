import asyncio
import pandas as pd
from blockchain_data import BlockchainDataFetcher
from quant_analysis import QuantAnalyzer
from trading_strategy import TradingStrategy
from datetime import datetime, timedelta

async def main():
    # Initialize components
    fetcher = BlockchainDataFetcher()
    analyzer = QuantAnalyzer(lookback_period=100)
    strategy = TradingStrategy(analyzer, risk_per_trade=0.02, min_confidence=0.7)
    
    # Fetch historical data for training
    print("Fetching historical data...")
    trades = await fetcher.get_dex_trades(pair='ETH/USDT', limit=1000)
    df = pd.DataFrame(trades)
    
    # Prepare and analyze data
    df = analyzer.prepare_data(df)
    df = analyzer.add_technical_indicators(df)
    
    # Train both models
    print("Training models...")
    analyzer.train_model(df)
    strategy.train_strategy_model(df)
    
    # Generate and validate signals
    print("\nGenerating trading signals...")
    signals = strategy.generate_trade_signals(df)
    
    # Simulate trading
    print("\nSimulating trading strategy...")
    initial_capital = 100000  # $100,000 initial capital
    current_capital = initial_capital
    
    for signal in signals:
        # Calculate position parameters
        position_size, stop_loss, take_profit = strategy.calculate_position_size(signal, current_capital)
        
        print(f"\nSignal Generated:")
        print(f"Time: {signal.timestamp}")
        print(f"Type: {signal.signal_type.upper()}")
        print(f"Price: ${signal.price:.2f}")
        print(f"Confidence: {signal.confidence:.2f}")
        print(f"Position Size: {position_size:.4f}")
        print(f"Stop Loss: ${stop_loss:.2f}")
        print(f"Take Profit: ${take_profit:.2f}")
        
        # Update positions and check results
        closed_positions = strategy.update_positions(signal.price, signal.timestamp)
        
        for position in closed_positions:
            print(f"\nPosition Closed:")
            print(f"PnL: ${position['pnl']:.2f}")
            print(f"Reason: {position['close_reason']}")
            current_capital += position['pnl']
    
    print(f"\nFinal Capital: ${current_capital:.2f}")
    print(f"Total Return: {((current_capital - initial_capital) / initial_capital * 100):.2f}%")

if __name__ == "__main__":
    asyncio.run(main()) 