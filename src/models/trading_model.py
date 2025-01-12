import tensorflow as tf
import numpy as np
from typing import Tuple, Optional, Dict
from src.utils.logger import get_logger
from src.models.risk_management import RiskManager

logger = get_logger()

class TradingModel:
    def __init__(self, input_shape: Tuple[int, int]):
        self.model = self._build_model(input_shape)
        self.risk_manager = RiskManager()
        
    def _build_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        """Build and compile the model."""
        try:
            model = tf.keras.Sequential([
                # LSTM layers
                tf.keras.layers.LSTM(128, input_shape=input_shape, return_sequences=True),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.LSTM(64, return_sequences=False),
                tf.keras.layers.Dropout(0.2),
                
                # Dense layers
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dense(16, activation='relu'),
                tf.keras.layers.Dense(1, activation='linear')
            ])
            
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            return model
        except Exception as e:
            logger.error(f"Error building model: {str(e)}")
            raise
            
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        validation_data: Optional[Tuple[np.ndarray, np.ndarray]] = None,
        epochs: int = 100,
        batch_size: int = 32
    ) -> tf.keras.callbacks.History:
        """Train the model with early stopping."""
        try:
            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5
                )
            ]
            
            history = self.model.fit(
                X_train,
                y_train,
                validation_data=validation_data,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
            return history
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
            
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions with risk management."""
        try:
            predictions = self.model.predict(X)
            # Apply risk management rules
            safe_predictions = self.risk_manager.apply_risk_rules(predictions)
            return safe_predictions
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise
            
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance."""
        try:
            metrics = self.model.evaluate(X_test, y_test, verbose=0)
            return dict(zip(self.model.metrics_names, metrics))
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise 