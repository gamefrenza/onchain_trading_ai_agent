from typing import Dict, Any
import numpy as np

class PositionManager:
    def __init__(self, config: Dict[str, Any]):
        self.max_position_size = config['max_position_size']
        self.position_sizing_model = config['position_sizing_model']
        self.current_positions: Dict[str, Dict[str, Any]] = {}
        
    def calculate_position_size(
        self,
        symbol: str,
        confidence: float,
        portfolio_value: float,
        market_data: Dict[str, Any]
    ) -> float:
        """Calculate optimal position size based on multiple factors"""
        try:
            # Base position size on portfolio value and confidence
            base_size = portfolio_value * confidence * self.max_position_size
            
            # Adjust for volatility
            volatility_factor = self._calculate_volatility_factor(market_data)
            adjusted_size = base_size * volatility_factor
            
            # Check existing exposure
            total_exposure = self._calculate_total_exposure()
            available_capacity = 1 - total_exposure
            
            # Final position size
            final_size = min(
                adjusted_size,
                portfolio_value * available_capacity * self.max_position_size
            )
            
            return final_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            raise 