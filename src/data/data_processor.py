from typing import List, Dict, Union, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from src.utils.logger import get_logger
from src.models.indicators import TechnicalIndicators

logger = get_logger()

class DataProcessor:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.indicators = TechnicalIndicators()
        
    def process_raw_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process raw trading data and add technical indicators."""
        try:
            # Ensure required columns exist
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("Missing required columns in input data")
            
            # Add technical indicators
            df = self.indicators.add_all_indicators(df)
            
            # Handle missing values
            df = df.dropna()
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            return df
        except Exception as e:
            logger.error(f"Error processing raw data: {str(e)}")
            raise
            
    def prepare_model_data(
        self,
        df: pd.DataFrame,
        sequence_length: int = 60,
        target_column: str = 'close'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for model training."""
        try:
            # Scale features
            feature_columns = [col for col in df.columns if col not in ['timestamp']]
            scaled_data = self.scaler.fit_transform(df[feature_columns])
            
            # Create sequences
            X, y = [], []
            for i in range(sequence_length, len(scaled_data)):
                X.append(scaled_data[i-sequence_length:i])
                y.append(scaled_data[i, df.columns.get_loc(target_column)])
                
            return np.array(X), np.array(y)
        except Exception as e:
            logger.error(f"Error preparing model data: {str(e)}")
            raise
            
    def inverse_transform_predictions(
        self,
        predictions: np.ndarray,
        target_column: str = 'close'
    ) -> np.ndarray:
        """Convert scaled predictions back to original scale."""
        try:
            # Create dummy array for inverse transform
            dummy = np.zeros((len(predictions), len(self.scaler.scale_)))
            dummy[:, self.scaler.feature_names_.index(target_column)] = predictions
            
            # Inverse transform
            inverse_transformed = self.scaler.inverse_transform(dummy)
            return inverse_transformed[:, self.scaler.feature_names_.index(target_column)]
        except Exception as e:
            logger.error(f"Error inverse transforming predictions: {str(e)}")
            raise 
            
    def process_historical_data(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_column: str = 'close'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Process historical data for model training"""
        try:
            # Add technical indicators
            df = self.indicators.add_all_indicators(df)
            
            # Handle missing values and outliers
            df = self._clean_data(df)
            
            # Create features and target
            X = df[feature_columns].values
            y = df[target_column].values
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            return X_scaled, y
            
        except Exception as e:
            logger.error(f"Error processing historical data: {str(e)}")
            raise 