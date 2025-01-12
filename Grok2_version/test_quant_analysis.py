import unittest
import pandas as pd
import numpy as np
from quant_analysis import QuantAnalyzer, TradingSignal
from datetime import datetime, timedelta

class TestQuantAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = QuantAnalyzer(lookback_period=100)
        self.sample_data = self._create_sample_data()
        
    def _create_sample_data(self):
        """Create sample market data for testing"""
        dates = pd.date_range(start='2024-01-01', periods=200, freq='H')
        data = {
            'timestamp': dates,
            'price': np.random.normal(2000, 100, 200),
            'volume': np.random.normal(10, 2, 200)
        }
        return pd.DataFrame(data)
        
    def test_prepare_data(self):
        """Test data preparation functionality"""
        df = self.analyzer.prepare_data(self.sample_data)
        
        self.assertIn('timestamp', df.columns)
        self.assertIn('price', df.columns)
        self.assertIn('volume', df.columns)
        self.assertTrue(df['timestamp'].is_monotonic_increasing)
        
    def test_technical_indicators(self):
        """Test technical indicator calculations"""
        df = self.analyzer.prepare_data(self.sample_data)
        df = self.analyzer.add_technical_indicators(df)
        
        # Check if indicators are calculated
        self.assertIn('sma_20', df.columns)
        self.assertIn('rsi', df.columns)
        self.assertIn('macd', df.columns)
        
        # Verify indicator values
        self.assertTrue(all(df['sma_20'].notna()[20:]))
        self.assertTrue(all(df['rsi'].between(0, 100, inclusive='both')[14:]))
        
    def test_model_training(self):
        """Test AI model training"""
        df = self.analyzer.prepare_data(self.sample_data)
        df = self.analyzer.add_technical_indicators(df)
        
        self.analyzer.train_model(df)
        self.assertIsNotNone(self.analyzer.model)
        
    def test_signal_generation(self):
        """Test trading signal generation"""
        df = self.analyzer.prepare_data(self.sample_data)
        df = self.analyzer.add_technical_indicators(df)
        self.analyzer.train_model(df)
        
        signals = self.analyzer.generate_trading_signals(df)
        
        for signal in signals:
            self.assertIsInstance(signal, TradingSignal)
            self.assertIn(signal.signal_type, ['buy', 'sell'])
            self.assertTrue(0 <= signal.confidence <= 1)

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests() 