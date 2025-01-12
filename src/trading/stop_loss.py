from typing import Dict, Any
import numpy as np

class StopLossManager:
    def __init__(self, config: Dict[str, Any]):
        self.default_stop_loss = config['default_stop_loss']
        self.trailing_stop_enabled = config['trailing_stop_enabled']
        self.trailing_stop_distance = config['trailing_stop_distance']
        
    def calculate_stop_loss(
        self,
        entry_price: float,
        position_size: float,
        market_data: Dict[str, Any],
        risk_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate stop loss levels based on multiple factors"""
        try:
            # Calculate ATR-based stop loss
            atr = self._calculate_atr(market_data)
            atr_stop = entry_price - (atr * 2)
            
            # Calculate volatility-based stop loss
            volatility = np.std(market_data['close'])
            vol_stop = entry_price - (volatility * 1.5)
            
            # Use the more conservative stop loss
            stop_price = max(atr_stop, vol_stop)
            
            return {
                'stop_price': stop_price,
                'stop_distance': (entry_price - stop_price) / entry_price,
                'risk_amount': position_size * (entry_price - stop_price)
            }
            
        except Exception as e:
            logger.error(f"Error calculating stop loss: {str(e)}")
            raise 