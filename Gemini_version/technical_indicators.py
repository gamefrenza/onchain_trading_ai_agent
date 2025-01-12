import pandas as pd
import talib
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='technical_analysis.log'
)

class TechnicalAnalysis:
    def __init__(self, df):
        """
        Initialize with a DataFrame containing OHLCV data.
        DataFrame must have columns: 'Open', 'High', 'Low', 'Close', 'Volume'
        """
        try:
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"DataFrame must contain all OHLCV columns: {required_columns}")
            
            self.df = df.copy()
            # Convert to float type if needed
            for col in required_columns:
                self.df[col] = self.df[col].astype(float)
                
            logging.info("Successfully initialized TechnicalAnalysis")
            
        except Exception as e:
            logging.error(f"Initialization error: {str(e)}")
            raise

    def add_moving_averages(self, periods=[7, 21]):
        """
        Add Simple Moving Averages (SMA) and Exponential Moving Averages (EMA)
        for specified periods
        """
        try:
            for period in periods:
                # Simple Moving Average
                self.df[f'SMA_{period}'] = talib.SMA(self.df['Close'], timeperiod=period)
                
                # Exponential Moving Average
                self.df[f'EMA_{period}'] = talib.EMA(self.df['Close'], timeperiod=period)
                
            logging.info(f"Added Moving Averages for periods: {periods}")
            
        except Exception as e:
            logging.error(f"Error calculating Moving Averages: {str(e)}")
            raise

    def add_rsi(self, period=14):
        """
        Add Relative Strength Index (RSI)
        """
        try:
            self.df['RSI'] = talib.RSI(self.df['Close'], timeperiod=period)
            logging.info(f"Added RSI with period {period}")
            
        except Exception as e:
            logging.error(f"Error calculating RSI: {str(e)}")
            raise

    def add_macd(self, fast_period=12, slow_period=26, signal_period=9):
        """
        Add Moving Average Convergence Divergence (MACD)
        """
        try:
            macd, signal, hist = talib.MACD(
                self.df['Close'],
                fastperiod=fast_period,
                slowperiod=slow_period,
                signalperiod=signal_period
            )
            
            self.df['MACD'] = macd
            self.df['MACD_Signal'] = signal
            self.df['MACD_Hist'] = hist
            
            logging.info("Added MACD indicators")
            
        except Exception as e:
            logging.error(f"Error calculating MACD: {str(e)}")
            raise

    def add_bollinger_bands(self, period=20, num_std=2):
        """
        Add Bollinger Bands
        """
        try:
            upper, middle, lower = talib.BBANDS(
                self.df['Close'],
                timeperiod=period,
                nbdevup=num_std,
                nbdevdn=num_std,
                matype=0  # Simple Moving Average
            )
            
            self.df['BB_Upper'] = upper
            self.df['BB_Middle'] = middle
            self.df['BB_Lower'] = lower
            
            # Calculate Bandwidth and %B
            self.df['BB_Bandwidth'] = (upper - lower) / middle
            self.df['BB_%B'] = (self.df['Close'] - lower) / (upper - lower)
            
            logging.info(f"Added Bollinger Bands with period {period} and {num_std} standard deviations")
            
        except Exception as e:
            logging.error(f"Error calculating Bollinger Bands: {str(e)}")
            raise

    def add_all_indicators(self):
        """
        Add all technical indicators with default parameters
        """
        try:
            self.add_moving_averages()
            self.add_rsi()
            self.add_macd()
            self.add_bollinger_bands()
            logging.info("Successfully added all technical indicators")
            
        except Exception as e:
            logging.error(f"Error adding all indicators: {str(e)}")
            raise

    def get_dataframe(self):
        """
        Return the DataFrame with all added indicators
        """
        return self.df


def main():
    """
    Example usage of the TechnicalAnalysis class
    """
    try:
        # Create sample OHLCV data
        sample_data = {
            'Open': np.random.random(100) * 100,
            'High': np.random.random(100) * 100,
            'Low': np.random.random(100) * 100,
            'Close': np.random.random(100) * 100,
            'Volume': np.random.random(100) * 1000000
        }
        df = pd.DataFrame(sample_data)
        
        # Initialize technical analysis
        ta = TechnicalAnalysis(df)
        
        # Add all indicators
        ta.add_all_indicators()
        
        # Get resulting DataFrame
        result_df = ta.get_dataframe()
        
        # Display first few rows with all indicators
        print("\nFirst few rows of data with technical indicators:")
        print(result_df.head())
        
        # Display basic statistics
        print("\nBasic statistics of technical indicators:")
        print(result_df.describe())
        
        # Save to CSV
        output_file = 'technical_analysis_results.csv'
        result_df.to_csv(output_file)
        logging.info(f"Results saved to {output_file}")
        
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 