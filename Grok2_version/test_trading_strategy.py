import unittest
import pandas as pd
import numpy as np
from trading_strategy import TradingStrategy, PositionType, StrategyState
from quant_analysis import QuantAnalyzer
from datetime import datetime

class TestTradingStrategy(unittest.TestCase):
    def setUp(self):
        self.analyzer = QuantAnalyzer()
        self.strategy = TradingStrategy(
            quant_analyzer=self.analyzer,
            risk_per_trade=0.02,
            max_positions=3,
            min_confidence=0.7
        )
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
        
    def test_strategy_initialization(self):
        """Test strategy initialization"""
        self.assertEqual(self.strategy.risk_per_trade, 0.02)
        self.assertEqual(self.strategy.max_positions, 3)
        self.assertEqual(self.strategy.min_confidence, 0.7)
        self.assertEqual(len(self.strategy.current_positions), 0)
        
    def test_feature_preparation(self):
        """Test feature preparation for strategy model"""
        df = self.analyzer.prepare_data(self.sample_data)
        df = self.analyzer.add_technical_indicators(df)
        
        features = self.strategy._prepare_strategy_features(df)
        
        self.assertIn('price_volatility', features.columns)
        self.assertIn('volume_trend', features.columns)
        self.assertIn('rsi_trend', features.columns)
        
    def test_position_sizing(self):
        """Test position size calculation"""
        signal = self.analyzer.TradingSignal(
            timestamp=datetime.now(),
            symbol='ETH/USDT',
            signal_type='buy',
            confidence=0.8,
            indicators={},
            price=2000.0
        )
        
        position_size, stop_loss, take_profit = self.strategy.calculate_position_size(
            signal=signal,
            capital=10000.0
        )
        
        self.assertTrue(position_size > 0)
        self.assertTrue(stop_loss < signal.price)
        self.assertTrue(take_profit > signal.price)
        
    def test_position_management(self):
        """Test position management functionality"""
        # Add a test position
        position = StrategyState(
            position_type=PositionType.LONG,
            entry_price=2000.0,
            position_size=1.0,
            stop_loss=1900.0,
            take_profit=2200.0,
            entry_time=datetime.now()
        )
        self.strategy.current_positions.append(position)
        
        # Test stop loss
        closed_positions = self.strategy.update_positions(1890.0, datetime.now())
        self.assertEqual(len(closed_positions), 1)
        self.assertEqual(closed_positions[0]['close_reason'], 'stop_loss')
        
        # Test take profit
        self.strategy.current_positions.append(position)
        closed_positions = self.strategy.update_positions(2210.0, datetime.now())
        self.assertEqual(len(closed_positions), 1)
        self.assertEqual(closed_positions[0]['close_reason'], 'take_profit')

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests() 