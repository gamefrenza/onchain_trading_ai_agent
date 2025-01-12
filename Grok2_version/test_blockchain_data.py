import unittest
import asyncio
from unittest.mock import Mock, patch
from blockchain_data import BlockchainDataFetcher
import pandas as pd
from datetime import datetime

class TestBlockchainDataFetcher(unittest.TestCase):
    def setUp(self):
        self.fetcher = BlockchainDataFetcher()
        
    async def async_setup(self):
        """Async setup for tests that need it"""
        pass
        
    def test_init(self):
        """Test initialization of BlockchainDataFetcher"""
        self.assertIsNotNone(self.fetcher.eth_node)
        self.assertIsNotNone(self.fetcher.binance_client)
        
    @patch('web3.eth.Eth.get_block')
    async def test_get_latest_eth_transactions(self, mock_get_block):
        """Test fetching latest Ethereum transactions"""
        # Mock block data
        mock_block = {
            'transactions': [{
                'hash': b'123',
                'from': '0x123',
                'to': '0x456',
                'value': 1000000000000000000,  # 1 ETH
                'blockNumber': 1000
            }],
            'timestamp': int(datetime.now().timestamp())
        }
        mock_get_block.return_value = mock_block
        
        transactions = await self.fetcher.get_latest_eth_transactions(num_blocks=1)
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['value'], 1.0)  # 1 ETH
        
    @patch('ccxt.binance.fetch_trades')
    async def test_get_dex_trades(self, mock_fetch_trades):
        """Test fetching DEX trades"""
        mock_trades = [{
            'symbol': 'ETH/USDT',
            'price': 2000.0,
            'amount': 1.5,
            'side': 'buy',
            'timestamp': int(datetime.now().timestamp() * 1000)
        }]
        mock_fetch_trades.return_value = mock_trades
        
        trades = await self.fetcher.get_dex_trades(pair='ETH/USDT', limit=1)
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]['price'], 2000.0)
        
    def test_mempool_monitoring(self):
        """Test mempool monitoring functionality"""
        async def test_callback(tx):
            self.assertIn('hash', tx)
            self.assertIn('value', tx)
            
        async def run_test():
            with patch('web3.eth.Eth.filter') as mock_filter:
                mock_filter.return_value.get_new_entries.return_value = [b'0x123']
                with patch('web3.eth.Eth.get_transaction') as mock_get_tx:
                    mock_get_tx.return_value = {
                        'hash': b'0x123',
                        'from': '0x123',
                        'to': '0x456',
                        'value': 1000000000000000000,
                        'gasPrice': 20000000000
                    }
                    
                    # Run mempool monitoring for a short time
                    monitoring_task = asyncio.create_task(
                        self.fetcher.monitor_mempool(test_callback)
                    )
                    await asyncio.sleep(1)
                    monitoring_task.cancel()
                    
        asyncio.run(run_test())

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests() 