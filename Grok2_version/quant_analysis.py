import numpy as np
import pandas as pd
from typing import List, Dict, Union, Tuple
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import tensorflow as tf
from datetime import datetime, timedelta
import ta
from dataclasses import dataclass

@dataclass
class TradingSignal:
    timestamp: datetime
    symbol: str
    signal_type: str  # 'buy' or 'sell'
    confidence: float
    indicators: Dict[str, float]
    price: float

class QuantAnalyzer:
    def __init__(self, lookback_period: int = 100):
        self.lookback_period = lookback_period
        self.scaler = MinMaxScaler()
        self.model = None
        
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare and clean data for analysis"""
        df = data.copy()
        
        # Ensure required columns exist
        required_columns = ['timestamp', 'price', 'volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Data must contain columns: {required_columns}")
        
        # Convert timestamp to datetime if needed
        if not isinstance(df['timestamp'].iloc[0], datetime):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Remove duplicates and handle missing values
        df = df.drop_duplicates()
        df = df.fillna(method='ffill')
        
        return df

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical analysis indicators"""
        # Trend Indicators
        df['sma_20'] = ta.trend.sma_indicator(df['price'], window=20)
        df['sma_50'] = ta.trend.sma_indicator(df['price'], window=50)
        df['ema_20'] = ta.trend.ema_indicator(df['price'], window=20)
        
        # Momentum Indicators
        df['rsi'] = ta.momentum.rsi(df['price'], window=14)
        df['macd'] = ta.trend.macd_diff(df['price'])
        
        # Volatility Indicators
        df['bollinger_high'] = ta.volatility.bollinger_hband(df['price'])
        df['bollinger_low'] = ta.volatility.bollinger_lband(df['price'])
        df['atr'] = ta.volatility.average_true_range(df['price'], df['price'], df['price'])
        
        # Volume Indicators
        df['volume_sma'] = ta.volume.volume_weighted_average_price(
            high=df['price'],
            low=df['price'],
            close=df['price'],
            volume=df['volume']
        )
        
        return df

    def create_lstm_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Create LSTM model for pattern recognition"""
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            Dense(units=25),
            Dense(units=1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model

    def prepare_sequences(self, data: np.ndarray, sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM model"""
        X, y = [], []
        for i in range(len(data) - sequence_length):
            X.append(data[i:(i + sequence_length)])
            # Predict if price will increase (1) or decrease (0)
            y.append(1 if data[i + sequence_length][0] > data[i + sequence_length - 1][0] else 0)
        return np.array(X), np.array(y)

    def train_model(self, df: pd.DataFrame, sequence_length: int = 10) -> None:
        """Train the LSTM model on historical data"""
        # Prepare features
        features = ['price', 'volume', 'rsi', 'macd', 'sma_20', 'bollinger_high', 'bollinger_low']
        data = df[features].values
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(data)
        
        # Prepare sequences
        X, y = self.prepare_sequences(scaled_data, sequence_length)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create and train the model
        self.model = self.create_lstm_model((sequence_length, len(features)))
        self.model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_data=(X_test, y_test),
            verbose=0
        )

    def generate_trading_signals(self, df: pd.DataFrame) -> List[TradingSignal]:
        """Generate trading signals using both technical and AI analysis"""
        signals = []
        
        # Technical Analysis Signals
        df['sma_cross'] = (df['sma_20'] > df['sma_50']).astype(int)
        df['sma_cross_change'] = df['sma_cross'].diff()
        
        # RSI conditions
        oversold = df['rsi'] < 30
        overbought = df['rsi'] > 70
        
        # Bollinger Band conditions
        bb_lower_break = df['price'] < df['bollinger_low']
        bb_upper_break = df['price'] > df['bollinger_high']
        
        for i in range(len(df)):
            if i < self.lookback_period:
                continue
                
            current_price = df['price'].iloc[i]
            timestamp = df['timestamp'].iloc[i]
            
            # Combine technical signals
            tech_buy_signal = (
                df['sma_cross_change'].iloc[i] == 1 or
                (oversold.iloc[i] and bb_lower_break.iloc[i])
            )
            
            tech_sell_signal = (
                df['sma_cross_change'].iloc[i] == -1 or
                (overbought.iloc[i] and bb_upper_break.iloc[i])
            )
            
            # AI prediction (if model is trained)
            ai_confidence = 0.5
            if self.model is not None:
                recent_data = df[i-self.lookback_period:i][
                    ['price', 'volume', 'rsi', 'macd', 'sma_20', 'bollinger_high', 'bollinger_low']
                ].values
                scaled_data = self.scaler.transform(recent_data)
                prediction = self.model.predict(scaled_data.reshape(1, self.lookback_period, -1))[0][0]
                ai_confidence = prediction
            
            # Combine signals
            if tech_buy_signal and ai_confidence > 0.6:
                signals.append(TradingSignal(
                    timestamp=timestamp,
                    symbol=df.get('symbol', 'UNKNOWN'),
                    signal_type='buy',
                    confidence=ai_confidence,
                    indicators={
                        'rsi': df['rsi'].iloc[i],
                        'macd': df['macd'].iloc[i],
                        'sma_20': df['sma_20'].iloc[i],
                        'sma_50': df['sma_50'].iloc[i]
                    },
                    price=current_price
                ))
            elif tech_sell_signal and ai_confidence < 0.4:
                signals.append(TradingSignal(
                    timestamp=timestamp,
                    symbol=df.get('symbol', 'UNKNOWN'),
                    signal_type='sell',
                    confidence=1 - ai_confidence,
                    indicators={
                        'rsi': df['rsi'].iloc[i],
                        'macd': df['macd'].iloc[i],
                        'sma_20': df['sma_20'].iloc[i],
                        'sma_50': df['sma_50'].iloc[i]
                    },
                    price=current_price
                ))
                
        return signals

    def backtest_strategy(self, df: pd.DataFrame, initial_capital: float = 10000.0) -> Dict:
        """Backtest the trading strategy"""
        signals = self.generate_trading_signals(df)
        
        capital = initial_capital
        position = 0
        trades = []
        
        for signal in signals:
            if signal.signal_type == 'buy' and position == 0:
                position = capital / signal.price
                capital = 0
                trades.append({
                    'type': 'buy',
                    'price': signal.price,
                    'timestamp': signal.timestamp,
                    'position': position
                })
            elif signal.signal_type == 'sell' and position > 0:
                capital = position * signal.price
                position = 0
                trades.append({
                    'type': 'sell',
                    'price': signal.price,
                    'timestamp': signal.timestamp,
                    'capital': capital
                })
        
        # Calculate final position value
        final_value = capital + (position * df['price'].iloc[-1])
        roi = (final_value - initial_capital) / initial_capital * 100
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'roi_percent': roi,
            'num_trades': len(trades),
            'trades': trades
        } 