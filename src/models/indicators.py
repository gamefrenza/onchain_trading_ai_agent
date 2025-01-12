import pandas as pd
import numpy as np
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger()

class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        try:
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            raise
            
    @staticmethod
    def calculate_macd(
        data: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD and Signal line."""
        try:
            exp1 = data['close'].ewm(span=fast_period).mean()
            exp2 = data['close'].ewm(span=slow_period).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=signal_period).mean()
            return macd, signal
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            raise
            
    @staticmethod
    def calculate_bollinger_bands(
        data: pd.DataFrame,
        period: int = 20,
        std_dev: int = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands."""
        try:
            middle_band = data['close'].rolling(window=period).mean()
            std = data['close'].rolling(window=period).std()
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            return upper_band, middle_band, lower_band
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            raise
            
    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to the dataframe."""
        try:
            # Add RSI
            df['rsi'] = self.calculate_rsi(df)
            
            # Add MACD
            df['macd'], df['macd_signal'] = self.calculate_macd(df)
            df['macd_hist'] = df['macd'] - df['macd_signal']
            
            # Add Bollinger Bands
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = self.calculate_bollinger_bands(df)
            
            # Add momentum indicators
            df['momentum'] = df['close'].diff(periods=10)
            df['rate_of_change'] = df['close'].pct_change(periods=10)
            
            return df
        except Exception as e:
            logger.error(f"Error adding indicators: {str(e)}")
            raise 