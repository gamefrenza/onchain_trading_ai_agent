import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.models.trading_model import TradingModel
from src.utils.error_handler import ModelError

@pytest.fixture
def model():
    return TradingModel(input_shape=(60, 20))

@pytest.fixture
def sample_data():
    return np.random.random((32, 60, 20))  # batch_size, sequence_length, features

def test_model_initialization(model):
    """Test model initialization and architecture."""
    assert model.model is not None
    assert len(model.model.layers) > 0
    
@pytest.mark.asyncio
async def test_model_prediction(model, sample_data):
    """Test model prediction functionality."""
    predictions = await model.predict(sample_data)
    assert predictions.shape == (32, 1)
    assert np.all((predictions >= -1) & (predictions <= 1))

def test_model_training(model, sample_data):
    """Test model training process."""
    y = np.random.random((32, 1))
    history = model.train(sample_data, y, epochs=2)
    assert 'loss' in history.history
    assert 'mae' in history.history

@pytest.mark.asyncio
async def test_model_error_handling(model):
    """Test model error handling with invalid input."""
    with pytest.raises(ModelError):
        await model.predict(np.array([]))

def test_model_evaluation(model, sample_data):
    """Test model evaluation metrics."""
    y = np.random.random((32, 1))
    metrics = model.evaluate(sample_data, y)
    assert 'loss' in metrics
    assert 'mae' in metrics 