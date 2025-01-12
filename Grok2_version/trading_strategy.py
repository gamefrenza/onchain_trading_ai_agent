from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime
from enum import Enum
from quant_analysis import QuantAnalyzer, TradingSignal
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import tensorflow as tf

class PositionType(Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"

@dataclass
class StrategyState:
    position_type: PositionType
    entry_price: float
    position_size: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    
class TradingStrategy:
    def __init__(self, 
                 quant_analyzer: QuantAnalyzer,
                 risk_per_trade: float = 0.02,
                 max_positions: int = 3,
                 min_confidence: float = 0.7):
        """
        Initialize trading strategy with risk management parameters
        
        Args:
            quant_analyzer: Quantitative analysis instance
            risk_per_trade: Maximum risk per trade (as fraction of capital)
            max_positions: Maximum number of concurrent positions
            min_confidence: Minimum AI confidence score to enter trade
        """
        self.quant_analyzer = quant_analyzer
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.min_confidence = min_confidence
        self.current_positions: List[StrategyState] = []
        
        # Additional ML model for strategy refinement
        self.strategy_model = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        
    def train_strategy_model(self, historical_data: pd.DataFrame):
        """Train the strategy refinement model"""
        # Prepare features for strategy model
        features = self._prepare_strategy_features(historical_data)
        
        # Create labels (1 for profitable trades, 0 for losses)
        labels = self._create_profitability_labels(historical_data)
        
        # Scale features and train model
        scaled_features = self.scaler.fit_transform(features)
        self.strategy_model.fit(scaled_features, labels)
        
    def _prepare_strategy_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare advanced features for strategy model"""
        features = pd.DataFrame()
        
        # Price action features
        features['price_volatility'] = df['price'].rolling(20).std()
        features['price_momentum'] = df['price'].pct_change(5)
        
        # Volume features
        features['volume_trend'] = df['volume'].rolling(10).mean() / df['volume'].rolling(30).mean()
        
        # Technical indicator features
        features['rsi_trend'] = df['rsi'] - df['rsi'].shift(5)
        features['macd_histogram'] = df['macd']
        features['bb_position'] = (df['price'] - df['bollinger_low']) / (df['bollinger_high'] - df['bollinger_low'])
        
        # Market regime features
        features['trend_strength'] = abs(df['sma_20'] - df['sma_50']) / df['sma_50']
        
        return features.dropna()
    
    def _create_profitability_labels(self, df: pd.DataFrame) -> np.ndarray:
        """Create labels for strategy model training"""
        # Simple forward returns (can be enhanced with more sophisticated profit calculation)
        forward_returns = df['price'].pct_change(5).shift(-5)
        return (forward_returns > 0).astype(int)
    
    def generate_trade_signals(self, current_data: pd.DataFrame) -> List[TradingSignal]:
        """Generate trade signals using both AI models"""
        # Get base signals from quant analyzer
        base_signals = self.quant_analyzer.generate_trading_signals(current_data)
        
        # Refine signals using strategy model
        refined_signals = []
        
        for signal in base_signals:
            if self._validate_signal(signal, current_data):
                refined_signals.append(signal)
                
        return refined_signals
    
    def _validate_signal(self, signal: TradingSignal, current_data: pd.DataFrame) -> bool:
        """Validate trading signal using strategy model"""
        # Prepare features for current market conditions
        features = self._prepare_strategy_features(current_data).iloc[-1:]
        scaled_features = self.scaler.transform(features)
        
        # Get strategy model prediction
        strategy_confidence = self.strategy_model.predict_proba(scaled_features)[0][1]
        
        # Combine both AI models' confidence
        combined_confidence = (signal.confidence + strategy_confidence) / 2
        
        return (combined_confidence >= self.min_confidence and
                len(self.current_positions) < self.max_positions)
    
    def calculate_position_size(self, signal: TradingSignal, capital: float) -> Tuple[float, float, float]:
        """Calculate position size and risk parameters"""
        # Determine stop loss level (using ATR or fixed percentage)
        stop_loss_pct = 0.02  # 2% stop loss
        stop_loss = signal.price * (1 - stop_loss_pct if signal.signal_type == 'buy' else 1 + stop_loss_pct)
        
        # Calculate risk amount
        risk_amount = capital * self.risk_per_trade
        
        # Calculate position size based on risk
        position_size = risk_amount / (abs(signal.price - stop_loss))
        
        # Calculate take profit (2:1 risk-reward ratio)
        take_profit = signal.price + (2 * abs(signal.price - stop_loss))
        
        return position_size, stop_loss, take_profit
    
    def update_positions(self, current_price: float, current_time: datetime) -> List[Dict]:
        """Update and manage existing positions"""
        closed_positions = []
        
        for position in self.current_positions[:]:
            # Check stop loss and take profit
            if position.position_type == PositionType.LONG:
                if current_price <= position.stop_loss:
                    closed_positions.append(self._close_position(position, current_price, current_time, 'stop_loss'))
                elif current_price >= position.take_profit:
                    closed_positions.append(self._close_position(position, current_price, current_time, 'take_profit'))
            else:  # SHORT position
                if current_price >= position.stop_loss:
                    closed_positions.append(self._close_position(position, current_price, current_time, 'stop_loss'))
                elif current_price <= position.take_profit:
                    closed_positions.append(self._close_position(position, current_price, current_time, 'take_profit'))
                    
        return closed_positions
    
    def _close_position(self, position: StrategyState, current_price: float, 
                       current_time: datetime, reason: str) -> Dict:
        """Close a position and calculate results"""
        self.current_positions.remove(position)
        
        pnl = (current_price - position.entry_price) * position.position_size
        if position.position_type == PositionType.SHORT:
            pnl = -pnl
            
        return {
            'entry_price': position.entry_price,
            'exit_price': current_price,
            'position_type': position.position_type.value,
            'position_size': position.position_size,
            'entry_time': position.entry_time,
            'exit_time': current_time,
            'pnl': pnl,
            'close_reason': reason
        } 