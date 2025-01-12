import asyncio
import os
from dotenv import load_dotenv
from blockchain_data import BlockchainDataFetcher
from quant_analysis import QuantAnalyzer
from trading_strategy import TradingStrategy
from trade_executor import TradeExecutor

# Load environment variables
load_dotenv()

async def main():
    # Initialize components
    fetcher = BlockchainDataFetcher()
    analyzer = QuantAnalyzer(lookback_period=100)
    strategy = TradingStrategy(analyzer, risk_per_trade=0.02, min_confidence=0.7)
    
    executor = TradeExecutor(
        web3_provider=os.getenv('ETH_NODE_URL'),
        private_key=os.getenv('PRIVATE_KEY'),
        dex_router_address=os.getenv('DEX_ROUTER_ADDRESS'),
        max_slippage=0.005
    )
    
    # Token addresses (example using ETH/USDT pair)
    token_addresses = {
        'in': os.getenv('WETH_ADDRESS'),
        'out': os.getenv('USDT_ADDRESS')
    }
    
    # Start transaction monitoring in the background
    monitoring_task = asyncio.create_task(executor.monitor_transactions())
    
    try:
        while True:
            # Fetch latest market data
            trades = await fetcher.get_dex_trades(pair='ETH/USDT', limit=1000)
            df = analyzer.prepare_data(trades)
            df = analyzer.add_technical_indicators(df)
            
            # Generate trading signals
            signals = strategy.generate_trade_signals(df)
            
            # Execute new signals
            for signal in signals:
                logger.info(f"New signal generated: {signal.signal_type} at {signal.price}")
                
                # Execute the trade
                tx_hash = await executor.execute_signal(signal, token_addresses)
                if tx_hash:
                    logger.info(f"Trade executed: {tx_hash}")
                else:
                    logger.error("Trade execution failed")
            
            # Wait before next iteration
            await asyncio.sleep(60)  # Check for new signals every minute
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        monitoring_task.cancel()
        
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        monitoring_task.cancel()

if __name__ == "__main__":
    asyncio.run(main()) 