import pytest
from unittest.mock import Mock, patch
from src.services.trading_service import TradingService
from src.trading.strategy_manager import StrategyManager
from src.models.trading_model import TradingModel
from src.utils.error_handler import NetworkError, ContractError
import numpy as np

@pytest.fixture
async def trading_service():
    strategy_manager = Mock(spec=StrategyManager)
    model = Mock(spec=TradingModel)
    return TradingService(strategy_manager, model)

@pytest.mark.asyncio
async def test_complete_trade_execution(trading_service):
    """Test complete trade execution flow."""
    trade_params = {
        'symbol': 'ETH/USD',
        'amount': 1.0,
        'price': 2000.0,
        'action': 'buy'
    }
    
    # Mock dependencies
    trading_service.model.predict.return_value = np.array([0.75])
    trading_service.strategy_manager.execute_strategies.return_value = {
        'action': 'buy',
        'size': 1.0,
        'confidence': 0.8
    }
    
    result = await trading_service.execute_trade(trade_params)
    assert result['status'] == 'success'
    assert 'transaction_hash' in result

@pytest.mark.asyncio
async def test_network_retry_mechanism(trading_service):
    """Test network error retry mechanism."""
    trade_params = {
        'symbol': 'ETH/USD',
        'amount': 1.0,
        'price': 2000.0
    }
    
    # Mock network failure then success
    trading_service._fetch_market_data.side_effect = [
        NetworkError("Connection failed", "NETWORK_ERROR"),
        {'features': np.random.random((1, 20))}
    ]
    
    result = await trading_service.execute_trade(trade_params)
    assert result['status'] == 'success'
    assert trading_service._fetch_market_data.call_count == 2

@pytest.mark.asyncio
async def test_contract_interaction(trading_service):
    """Test smart contract interaction handling."""
    with patch('web3.eth.Eth.send_raw_transaction') as mock_send:
        mock_send.return_value = '0x123'
        result = await trading_service._execute_transaction(
            {'amount': 1.0},
            {'action': 'buy'}
        )
        assert result['transaction_hash'] == '0x123' 