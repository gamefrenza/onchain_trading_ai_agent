from src.trading.strategy import TradingStrategy

class TrendFollowingStrategy(TradingStrategy):
    def __init__(self, model, risk_manager, trend_period: int = 20):
        super().__init__(model, risk_manager)
        self.trend_period = trend_period
        
    def execute_strategy(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            # Get pattern analysis
            patterns = self.analyze_patterns(market_data)
            
            # Calculate trend signals
            trend_signals = self._calculate_trend_signals(market_data)
            
            # Combine signals with AI patterns
            confidence = self._calculate_confidence(patterns, trend_signals)
            
            if confidence < self.min_confidence:
                return None
                
            # Determine position size
            position_size = self.risk_manager.calculate_position_size(
                patterns['prediction'],
                confidence,
                market_data['portfolio_value']
            )
            
            return {
                'action': 'buy' if patterns['trend_direction'] > 0 else 'sell',
                'size': position_size,
                'confidence': confidence,
                'stop_loss': self._calculate_stop_loss(market_data, patterns)
            }
        except Exception as e:
            logger.error(f"Error executing trend following strategy: {str(e)}")
            raise 