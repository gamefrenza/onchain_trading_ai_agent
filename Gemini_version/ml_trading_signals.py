import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
import logging
from technical_indicators import TechnicalAnalysis

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ml_trading.log'
)

class MLSignalGenerator:
    def __init__(self, df):
        """
        Initialize with a DataFrame containing price data and technical indicators
        """
        try:
            self.df = df.copy()
            self.prepare_features()
            logging.info("Successfully initialized MLSignalGenerator")
            
        except Exception as e:
            logging.error(f"Initialization error: {str(e)}")
            raise

    def generate_labels(self, forward_window=5):
        """
        Generate trading signals based on future price movements
        1 for buy (price goes up), 0 for sell (price goes down)
        """
        try:
            # Calculate future returns
            future_returns = self.df['Close'].shift(-forward_window) / self.df['Close'] - 1
            
            # Create binary labels: 1 for positive returns, 0 for negative
            self.df['target'] = (future_returns > 0).astype(int)
            
            # Remove rows with NaN values created by the shift
            self.df = self.df.dropna()
            
            logging.info(f"Generated labels using {forward_window}-day forward returns")
            
        except Exception as e:
            logging.error(f"Error generating labels: {str(e)}")
            raise

    def prepare_features(self):
        """
        Prepare feature set for machine learning
        """
        try:
            # Create features from technical indicators
            self.feature_columns = [
                # Moving Averages
                'SMA_7', 'SMA_21', 'EMA_7', 'EMA_21',
                # RSI
                'RSI',
                # MACD
                'MACD', 'MACD_Signal', 'MACD_Hist',
                # Bollinger Bands
                'BB_Bandwidth', 'BB_%B'
            ]
            
            # Add some additional features
            self.df['SMA_ratio'] = self.df['SMA_7'] / self.df['SMA_21']
            self.df['EMA_ratio'] = self.df['EMA_7'] / self.df['EMA_21']
            
            self.feature_columns.extend(['SMA_ratio', 'EMA_ratio'])
            
            # Remove any rows with NaN values
            self.df = self.df.dropna()
            
            logging.info("Prepared features for machine learning")
            
        except Exception as e:
            logging.error(f"Error preparing features: {str(e)}")
            raise

    def train_model(self, model_type='logistic', test_size=0.2, random_state=42):
        """
        Train a machine learning model on the prepared data
        """
        try:
            X = self.df[self.feature_columns]
            y = self.df['target']
            
            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Scale the features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Select and train model
            if model_type == 'logistic':
                model = LogisticRegression(random_state=random_state, max_iter=1000)
                model_name = "Logistic Regression"
            else:  # SVM
                model = SVC(random_state=random_state, probability=True)
                model_name = "Support Vector Machine"
            
            # Train the model
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate probabilities
            y_prob = model.predict_proba(X_test_scaled)[:, 1]
            
            # Store results
            self.model = model
            self.scaler = scaler
            self.X_test = X_test
            self.y_test = y_test
            self.y_pred = y_pred
            self.y_prob = y_prob
            
            logging.info(f"Successfully trained {model_name} model")
            
            return model, scaler
            
        except Exception as e:
            logging.error(f"Error training model: {str(e)}")
            raise

    def evaluate_model(self):
        """
        Evaluate the model's performance
        """
        try:
            # Generate classification report
            report = classification_report(self.y_test, self.y_pred)
            
            # Generate confusion matrix
            conf_matrix = confusion_matrix(self.y_test, self.y_pred)
            
            # Calculate additional trading-specific metrics
            accuracy = (conf_matrix[0,0] + conf_matrix[1,1]) / conf_matrix.sum()
            precision = conf_matrix[1,1] / (conf_matrix[1,1] + conf_matrix[0,1])
            recall = conf_matrix[1,1] / (conf_matrix[1,1] + conf_matrix[1,0])
            
            results = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'confusion_matrix': conf_matrix,
                'classification_report': report
            }
            
            logging.info("Model evaluation completed")
            return results
            
        except Exception as e:
            logging.error(f"Error evaluating model: {str(e)}")
            raise

    def generate_trading_signals(self, confidence_threshold=0.6):
        """
        Generate trading signals for the test set with confidence threshold
        """
        try:
            signals = pd.DataFrame(index=self.X_test.index)
            signals['probability'] = self.y_prob
            signals['predicted'] = self.y_pred
            signals['actual'] = self.y_test
            
            # Generate signals based on probability threshold
            signals['signal'] = 'HOLD'
            signals.loc[self.y_prob >= confidence_threshold, 'signal'] = 'BUY'
            signals.loc[self.y_prob <= (1 - confidence_threshold), 'signal'] = 'SELL'
            
            logging.info("Generated trading signals with confidence threshold")
            return signals
            
        except Exception as e:
            logging.error(f"Error generating trading signals: {str(e)}")
            raise


def main():
    """
    Example usage of the MLSignalGenerator class
    """
    try:
        # Create sample data using the TechnicalAnalysis class
        sample_data = {
            'Open': np.random.random(1000) * 100,
            'High': np.random.random(1000) * 100,
            'Low': np.random.random(1000) * 100,
            'Close': np.random.random(1000) * 100,
            'Volume': np.random.random(1000) * 1000000
        }
        df = pd.DataFrame(sample_data)
        
        # Add technical indicators
        ta = TechnicalAnalysis(df)
        ta.add_all_indicators()
        df_with_indicators = ta.get_dataframe()
        
        # Initialize ML signal generator
        ml_signals = MLSignalGenerator(df_with_indicators)
        
        # Generate labels
        ml_signals.generate_labels(forward_window=5)
        
        # Train model
        ml_signals.train_model(model_type='logistic')
        
        # Evaluate model
        results = ml_signals.evaluate_model()
        
        # Generate trading signals
        signals = ml_signals.generate_trading_signals(confidence_threshold=0.6)
        
        # Print results
        print("\nModel Evaluation Results:")
        print("-------------------------")
        print(f"Accuracy: {results['accuracy']:.2f}")
        print(f"Precision: {results['precision']:.2f}")
        print(f"Recall: {results['recall']:.2f}")
        print("\nConfusion Matrix:")
        print(results['confusion_matrix'])
        print("\nClassification Report:")
        print(results['classification_report'])
        
        # Save signals to CSV
        signals.to_csv('trading_signals.csv')
        logging.info("Results saved to trading_signals.csv")
        
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 