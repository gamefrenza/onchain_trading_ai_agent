import numpy as np
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger()

class RiskManager:
    def __init__(self, max_position_size: float = 0.1, stop_loss: float = 0.02):
        self.max_position_size = max_position_size  # Maximum position size as % of portfolio
        self.stop_loss = stop_loss  # Stop loss as % of position
        
    def calculate_position_size(
        self,
        prediction: float,
        confidence: float,
        portfolio_value: float
    ) -> float:
        """Calculate position size based on prediction confidence and risk parameters."""
        try:
            # Base position size on confidence and max position size
            position_size = min(
                confidence * self.max_position_size,
                self.max_position_size
            ) * portfolio_value
            return position_size
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            raise
            
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