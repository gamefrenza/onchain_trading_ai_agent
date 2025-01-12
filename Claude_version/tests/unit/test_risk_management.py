import pytest
import numpy as np
from src.models.risk_management import RiskManager
from src.utils.error_handler import ValidationError

@pytest.fixture
def risk_manager():
    return RiskManager(max_position_size=0.1, stop_loss=0.02)

def test_position_size_calculation(risk_manager):
    """Test position size calculation."""
    size = risk_manager.calculate_position_size(
        prediction=0.8,
        confidence=0.9,
        portfolio_value=10000
    )
    assert 0 < size <= 1000  # Max 10% of portfolio
    
def test_stop_loss_calculation(risk_manager):
    """Test stop loss calculation."""
    entry_price = 100
    stop_loss = risk_manager.calculate_stop_loss(entry_price)
    assert stop_loss == 98  # 2% below entry price

def test_risk_rules_application(risk_manager):
    """Test risk rules application to predictions."""
    predictions = np.array([0.1, -0.2, 0.8, -0.9])
    safe_predictions = risk_manager.apply_risk_rules(predictions)
    assert np.all(np.abs(safe_predictions) <= 0.05)  # Max 5% movement

def test_trade_validation(risk_manager):
    """Test trade validation rules."""
    current_positions = {
        'pos1': {'value': 1000},
        'pos2': {'value': 1000}
    }
    
    # Test maximum positions limit
    result = risk_manager.validate_trade(
        prediction=0.5,
        current_positions=current_positions,
        portfolio_value=10000
    )
    assert result is True
    
    # Test portfolio exposure limit
    large_positions = {
        'pos1': {'value': 8000},
        'pos2': {'value': 1000}
    }
    result = risk_manager.validate_trade(
        prediction=0.5,
        current_positions=large_positions,
        portfolio_value=10000
    )
    assert result is False 