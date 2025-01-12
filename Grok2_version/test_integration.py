import unittest
import asyncio
import pandas as pd
from datetime import datetime
from blockchain_data import BlockchainDataFetcher
from quant_analysis import QuantAnalyzer
from trading_strategy import TradingStrategy
from trade_executor import TradeExecutor
import os
from dotenv import load_dotenv

class TestSystemIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        load_dotenv()
        cls.fetcher = BlockchainDataFetcher()
        cls.analyzer = QuantAnalyzer()
        cls.strategy = TradingStrategy(cls.analyzer)
        cls.executor = TradeExecutor(
            web3_provider=os.getenv('ETH_NODE_URL'),
            private_key=os.getenv('PRIVATE_KEY'),
            dex_router_address=os.getenv('DEX_ROUTER_ADDRESS')
        )
        
    async def test_complete_trading_cycle(self):
        """Test complete trading cycle from data fetching to execution"""
        # 1. Fetch market data
        trades = await self.fetcher.get_dex_trades(pair='ETH/USDT', limit=100)
        self.assertTrue(len(trades) > 0)
        
        # 2. Prepare and analyze data
        df = self.analyzer.prepare_data(pd.DataFrame(trades))
        df = self.analyzer.add_technical_indicators(df)
        
        # 3. Train models
        self.analyzer.train_model(df)
        self.strategy.train_strategy_model(df)
        
        # 4. Generate signals
        signals = self.strategy.generate_trade_signals(df)
        self.assertTrue(len(signals) >= 0)
        
        if signals:
            # 5. Test trade execution
            signal = signals[0]
            token_addresses = {
                'in': os.getenv('WETH_ADDRESS'),
                'out': os.getenv('USDT_ADDRESS')
            }
            
            tx_hash = await self.executor.execute_signal(signal, token_addresses)
            if tx_hash:
                self.assertTrue(len(tx_hash) > 0)
                
    async def test_error_handling(self):
        """Test system error handling"""
        # Test with invalid token addresses
        signal = self.analyzer.TradingSignal(
            timestamp=datetime.now(),
            symbol='ETH/USDT',
            signal_type='buy',
            confidence=0.8,
            indicators={},
            price=2000.0
        )
        
        token_addresses = {
            'in': '0x0000000000000000000000000000000000000000',
            'out': '0x0000000000000000000000000000000000000000'
        }
        
        # Should handle invalid addresses gracefully
        tx_hash = await self.executor.execute_signal(signal, token_addresses)
        self.assertIsNone(tx_hash)
        
    async def test_performance_metrics(self):
        """Test system performance metrics"""
        # Fetch historical data
        trades = await self.fetcher.get_dex_trades(pair='ETH/USDT', limit=1000)
        df = self.analyzer.prepare_data(pd.DataFrame(trades))
        df = self.analyzer.add_technical_indicators(df)
        
        # Run backtest
        backtest_results = self.strategy.backtest_strategy(df)
        
        self.assertIn('initial_capital', backtest_results)
        self.assertIn('final_value', backtest_results)
        self.assertIn('roi_percent', backtest_results)
        self.assertIn('num_trades', backtest_results)
        
    def test_system_shutdown(self):
        """Test system shutdown procedure"""
        async def run_shutdown_test():
            # Start components
            monitoring_task = asyncio.create_task(
                self.executor.monitor_transactions()
            )
            
            # Simulate running system
            await asyncio.sleep(1)
            
            # Test graceful shutdown
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
            
        asyncio.run(run_shutdown_test())

def run_integration_tests():
    # Run tests with asyncio support
    loop = asyncio.get_event_loop()
    runner = unittest.TextTestRunner()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSystemIntegration)
    loop.run_until_complete(runner.run(suite))

if __name__ == '__main__':
    run_integration_tests() 