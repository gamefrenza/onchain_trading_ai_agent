import asyncio
from blockchain_data import BlockchainDataFetcher
from quant_analysis import QuantAnalyzer
from trading_strategy import TradingStrategy
from trade_executor import TradeExecutor
from monitoring import SystemMonitor, PerformanceMonitor
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from functools import wraps
from time import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MonitoredTradingAgent:
    def __init__(self):
        load_dotenv()
        
        # Initialize components
        self.fetcher = BlockchainDataFetcher()
        self.analyzer = QuantAnalyzer()
        self.strategy = TradingStrategy(self.analyzer)
        self.executor = TradeExecutor(
            web3_provider=os.getenv('ETH_NODE_URL'),
            private_key=os.getenv('PRIVATE_KEY'),
            dex_router_address=os.getenv('DEX_ROUTER_ADDRESS')
        )
        
        # Initialize monitoring
        self.system_monitor = SystemMonitor()
        self.performance_monitor = PerformanceMonitor()
        
        # Trading state
        self.is_running = False
        self.current_capital = float(os.getenv('INITIAL_CAPITAL', 10000))
        
        # Add input validation
        self._validate_config()
        
        # Add secure key handling
        self.private_key = self._load_private_key()
        
    def _validate_config(self):
        """Validate configuration parameters"""
        required_vars = ['ETH_NODE_URL', 'PRIVATE_KEY', 'DEX_ROUTER_ADDRESS']
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Missing required config: {var}")
                
    async def start(self):
        """Start the trading agent"""
        self.is_running = True
        logger.info("Starting AI trading agent...")
        
        try:
            while self.is_running:
                await self.trading_cycle()
                await asyncio.sleep(60)  # Wait between cycles
                
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
            self.is_running = False
            
    async def trading_cycle(self):
        """Execute one trading cycle"""
        try:
            async with timeout(30):  # Add timeout
                await self._execute_cycle()
        except TimeoutError:
            logger.error("Trading cycle timeout")
        except web3.exceptions.ContractLogicError as e:
            logger.error(f"Contract error: {str(e)}")
        except Exception as e:
            logger.error(f"Trading error: {str(e)}")
        
    async def _execute_cycle(self):
        """Execute one trading cycle"""
        try:
            # Update monitoring metrics
            self.system_monitor.update_capital(self.current_capital)
            self.system_monitor.update_positions(len(self.executor.current_positions))
            
            # Fetch and analyze market data
            with self.system_monitor.measure_signal_latency():
                trades = await self.fetcher.get_dex_trades(pair='ETH/USDT', limit=1000)
                signals = self.strategy.generate_trade_signals(trades)
            
            # Execute trades
            for signal in signals:
                with self.system_monitor.measure_execution_latency():
                    tx_hash = await self.executor.execute_signal(
                        signal,
                        {
                            'in': os.getenv('WETH_ADDRESS'),
                            'out': os.getenv('USDT_ADDRESS')
                        }
                    )
                
                if tx_hash:
                    self.system_monitor.record_trade(
                        signal.signal_type,
                        'success'
                    )
                    logger.info(f"Trade executed: {tx_hash}")
                else:
                    self.system_monitor.record_trade(
                        signal.signal_type,
                        'failed'
                    )
                    logger.error("Trade execution failed")
            
            # Update performance metrics
            for position in self.executor.executed_trades:
                self.performance_monitor.record_trade(position)
                self.current_capital += position['pnl']
                self.system_monitor.update_profit(position['pnl'])
                
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
            
    def stop(self):
        """Stop the trading agent"""
        self.is_running = False
        logger.info("Stopping AI trading agent...")

async def main():
    agent = MonitoredTradingAgent()
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        agent.stop()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        agent.stop()

if __name__ == "__main__":
    asyncio.run(main()) 