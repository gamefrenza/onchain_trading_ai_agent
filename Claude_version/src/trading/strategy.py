from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import numpy as np
from src.utils.logger import get_logger
from src.models.trading_model import TradingModel
from src.models.risk_management import RiskManager

logger = get_logger()

class TradingStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(
        self,
        model: TradingModel,
        risk_manager: RiskManager,
        min_confidence: float = 0.6
    ):
        self.model = model
        self.risk_manager = risk_manager
        self.min_confidence = min_confidence
        self.positions: Dict[str, Any] = {}
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_return': 0.0
        }
        
    @abstractmethod
    def generate_signals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals based on market data."""
        pass
        
    @abstractmethod
    def calculate_confidence(self, signals: Dict[str, Any]) -> float:
        """Calculate confidence score for signals."""
        pass
        
    def execute_strategy(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute trading strategy and return trade decision."""
        try:
            # Generate signals
            signals = self.generate_signals(market_data)
            
            # Calculate confidence
            confidence = self.calculate_confidence(signals)
            
            if confidence < self.min_confidence:
                return None
                
            # Get model prediction
            prediction = self.model.predict(market_data['features'])
            
            # Apply risk management
            if not self.risk_manager.validate_trade(
                prediction,
                self.positions,
                market_data['portfolio_value']
            ):
                return None
                
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                prediction,
                confidence,
                market_data['portfolio_value']
            )
            
            # Generate trade decision
            return {
                'action': 'buy' if prediction > 0 else 'sell',
                'size': position_size,
                'confidence': confidence,
                'signals': signals,
                'stop_loss': self.risk_manager.calculate_stop_loss(
                    market_data['current_price']
                )
            }
        except Exception as e:
            logger.error(f"Error executing strategy: {str(e)}")
            raise

    def analyze_patterns(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze patterns using AI model predictions"""
        try:
            # Get model prediction
            prediction = self.model.predict(market_data['features'])
            
            # Analyze prediction patterns
            pattern_strength = np.abs(prediction).mean()
            trend_direction = np.sign(prediction).sum() / len(prediction)
            
            # Analyze volatility
            volatility = np.std(market_data['close'])
            
            return {
                'pattern_strength': float(pattern_strength),
                'trend_direction': float(trend_direction),
                'volatility': float(volatility),
                'prediction': float(prediction[-1])
            }
        except Exception as e:
            logger.error(f"Error analyzing patterns: {str(e)}")
            raise


class MACDStrategy(TradingStrategy):
    """MACD-based trading strategy."""
    
    def generate_signals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            macd = market_data['indicators']['macd']
            signal = market_data['indicators']['macd_signal']
            
            # Calculate crossover signals
            crossover = np.diff(np.signbit(macd - signal)).astype(bool)
            golden_cross = crossover & (macd > signal)
            death_cross = crossover & (macd < signal)
            
            return {
                'macd_value': macd[-1],
                'signal_value': signal[-1],
                'golden_cross': golden_cross[-1],
                'death_cross': death_cross[-1],
                'trend_strength': abs(macd[-1] - signal[-1])
            }
        except Exception as e:
            logger.error(f"Error generating MACD signals: {str(e)}")
            raise
            
    def calculate_confidence(self, signals: Dict[str, Any]) -> float:
        try:
            # Base confidence on trend strength and signal clarity
            trend_confidence = min(abs(signals['trend_strength']) / 0.01, 1.0)
            signal_confidence = 1.0 if signals['golden_cross'] or signals['death_cross'] else 0.5
            
            return trend_confidence * signal_confidence
        except Exception as e:
            logger.error(f"Error calculating MACD confidence: {str(e)}")
            raise


class RSIStrategy(TradingStrategy):
    """RSI-based trading strategy."""
    
    def __init__(self, *args, oversold: int = 30, overbought: int = 70, **kwargs):
        super().__init__(*args, **kwargs)
        self.oversold = oversold
        self.overbought = overbought
        
    def generate_signals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            rsi = market_data['indicators']['rsi']
            
            return {
                'rsi_value': rsi[-1],
                'oversold': rsi[-1] < self.oversold,
                'overbought': rsi[-1] > self.overbought,
                'trend_direction': 1 if rsi[-1] > rsi[-2] else -1,
                'trend_strength': abs(rsi[-1] - 50) / 50
            }
        except Exception as e:
            logger.error(f"Error generating RSI signals: {str(e)}")
            raise
            
    def calculate_confidence(self, signals: Dict[str, Any]) -> float:
        try:
            # Base confidence on distance from neutral (50) and trend strength
            base_confidence = signals['trend_strength']
            
            # Increase confidence for extreme conditions
            if signals['oversold'] or signals['overbought']:
                base_confidence *= 1.2
                
            return min(base_confidence, 1.0)
        except Exception as e:
            logger.error(f"Error calculating RSI confidence: {str(e)}")
            raise 