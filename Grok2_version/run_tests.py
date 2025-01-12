import unittest
import asyncio
from test_blockchain_data import TestBlockchainDataFetcher
from test_quant_analysis import TestQuantAnalyzer
from test_trading_strategy import TestTradingStrategy
from test_integration import TestSystemIntegration

def run_all_tests():
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBlockchainDataFetcher))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQuantAnalyzer))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTradingStrategy))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSystemIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    run_all_tests() 