import tensorflow as tf
from typing import Tuple, Dict, Any
import numpy as np

class TradingModel:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = self._build_model()
        
    def _build_model(self) -> tf.keras.Model:
        """Build deep learning model architecture"""
        model = tf.keras.Sequential([
            # CNN layers for pattern recognition
            tf.keras.layers.Conv1D(64, 3, activation='relu', input_shape=self.config['input_shape']),
            tf.keras.layers.MaxPooling1D(2),
            tf.keras.layers.Conv1D(128, 3, activation='relu'),
            tf.keras.layers.MaxPooling1D(2),
            
            # LSTM layers for temporal patterns
            tf.keras.layers.LSTM(128, return_sequences=True),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(64),
            
            # Dense layers for final prediction
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='tanh')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.config['learning_rate']),
            loss=self.config['loss_function'],
            metrics=['mae', 'mse']
        )
        return model 