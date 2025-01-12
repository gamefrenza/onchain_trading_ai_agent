import numpy as np
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger()

class RiskManager:
    def __init__(self, config: Dict[str, Any]):
        self.max_position_size = config['max_position_size']
        self.max_drawdown = config['max_drawdown']
        self.stop_loss = config['stop_loss']
        
    def calculate_position_size(
        self,
        prediction: float,
        confidence: float,
        current_price: float,
        portfolio_value: float
    ) -> float:
        """Calculate safe position size based on risk parameters"""
        # Base position size on prediction confidence
        base_size = portfolio_value * confidence * self.max_position_size
        
        # Apply risk limits
        position_size = min(
            base_size,
            portfolio_value * self.max_position_size,
            portfolio_value / current_price
        )
        
        return position_size
        
    def calculate_stop_loss(self, entry_price: float) -> float:
        """Calculate stop loss price."""
        return entry_price * (1 - self.stop_loss)
        
    def apply_risk_rules(self, predictions: np.ndarray) -> np.ndarray:
        """Apply risk management rules to predictions."""
        try:
            # Implement risk rules (e.g., limit maximum predicted movement)
            max_movement = 0.05  # 5% maximum predicted price movement
            return np.clip(predictions, -max_movement, max_movement)
        except Exception as e:
            logger.error(f"Error applying risk rules: {str(e)}")
            raise
            
    def validate_trade(
        self,
        prediction: float,
        current_positions: Dict[str, Any],
        portfolio_value: float
    ) -> bool:
        """Validate if a trade meets risk management criteria."""
        try:
            # Check if we have too many open positions
            if len(current_positions) >= 5:  # Maximum number of concurrent positions
                return False
                
            # Check if we have enough portfolio value available
            total_exposure = sum(pos['value'] for pos in current_positions.values())
            if total_exposure / portfolio_value > 0.8:  # Maximum 80% portfolio exposure
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error validating trade: {str(e)}")
            raise 