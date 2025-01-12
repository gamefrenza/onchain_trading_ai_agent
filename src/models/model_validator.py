from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
from typing import Dict

class ModelValidator:
    def __init__(self, validation_data: np.ndarray, validation_targets: np.ndarray):
        self.validation_data = validation_data
        self.validation_targets = validation_targets
        
    def validate_model(self, model) -> Dict[str, float]:
        """Validate model performance"""
        predictions = model.predict(self.validation_data)
        
        metrics = {
            'mse': mean_squared_error(self.validation_targets, predictions),
            'mae': mean_absolute_error(self.validation_targets, predictions),
            'rmse': np.sqrt(mean_squared_error(self.validation_targets, predictions)),
            'directional_accuracy': self._calculate_directional_accuracy(
                self.validation_targets, predictions
            )
        }
        
        return metrics 