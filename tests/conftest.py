import pytest
import numpy as np
from unittest.mock import Mock
from web3 import Web3

@pytest.fixture
def web3_mock():
    """Create a mock Web3 instance."""
    w3 = Mock(spec=Web3)
    w3.eth.contract.return_value = Mock()
    w3.eth.get_block_number.return_value = 1000
    return w3

@pytest.fixture
def market_data():
    """Generate sample market data."""
    return {
        'timestamp': np.array([1, 2, 3, 4, 5]),
        'open': np.random.random(5),
        'high': np.random.random(5),
        'low': np.random.random(5),
        'close': np.random.random(5),
        'volume': np.random.random(5)
    }

@pytest.fixture
def mock_strategy_manager():
    """Create a mock strategy manager."""
    manager = Mock()
    manager.execute_strategies.return_value = {
        'action': 'buy',
        'size': 1.0,
        'confidence': 0.8
    }
    return manager 