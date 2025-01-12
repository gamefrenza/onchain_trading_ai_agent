from typing import Dict, List, Any
import numpy as np
from src.utils.logger import get_logger
from src.trading.strategy import TradingStrategy
from src.models.risk_management import RiskManager

logger = get_logger()

class StrategyManager:
    def __init__(self, portfolio_value: float):
        self.strategies: Dict[str, TradingStrategy] = {}
        self.portfolio_value = portfolio_value
        self.performance_metrics: Dict[str, List[float]] = {}
        
    def add_strategy(self, name: str, strategy: TradingStrategy) -> None:
        """Add a trading strategy to the manager."""
        try:
            self.strategies[name] = strategy
            self.performance_metrics[name] = []
            logger.info(f"Added strategy: {name}")
        except Exception as e:
            logger.error(f"Error adding strategy: {str(e)}")
            raise
            
    def update_portfolio_value(self, value: float) -> None:
        """Update current portfolio value."""
        self.portfolio_value = value
        
    async def execute_strategies(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all strategies and combine results."""
        try:
            decisions = {}
            weighted_decision = {
                'action': None,
                'size': 0,
                'confidence': 0
            }
            
            for name, strategy in self.strategies.items():
                decision = strategy.execute_strategy({
                    **market_data,
                    'portfolio_value': self.portfolio_value
                })
                
                if decision:
                    decisions[name] = decision
                    
                    # Weight decision by strategy performance
                    weight = self._calculate_strategy_weight(name)
                    weighted_decision['size'] += decision['size'] * weight
                    weighted_decision['confidence'] = max(
                        weighted_decision['confidence'],
                        decision['confidence'] * weight
                    )
            
            if decisions:
                # Determine final action based on weighted consensus
                buy_confidence = sum(
                    d['confidence'] for d in decisions.values()
                    if d['action'] == 'buy'
                )
                sell_confidence = sum(
                    d['confidence'] for d in decisions.values()
                    if d['action'] == 'sell'
                )
                
                weighted_decision['action'] = 'buy' if buy_confidence > sell_confidence else 'sell'
                
                return weighted_decision
            
            return None
        except Exception as e:
            logger.error(f"Error executing strategies: {str(e)}")
            raise
            
    def update_performance(self, strategy_name: str, return_pct: float) -> None:
        """Update strategy performance metrics."""
        try:
            self.performance_metrics[strategy_name].append(return_pct)
            logger.info(f"Updated performance for {strategy_name}: {return_pct:.2%}")
        except Exception as e:
            logger.error(f"Error updating performance: {str(e)}")
            raise
            
    def _calculate_strategy_weight(self, strategy_name: str) -> float:
        """Calculate strategy weight based on historical performance."""
        try:
            metrics = self.performance_metrics[strategy_name]
            if not metrics:
                return 1.0 / len(self.strategies)
                
            # Calculate Sharpe ratio-like metric
            returns = np.array(metrics)
            return max(0, np.mean(returns) / (np.std(returns) + 1e-6))
        except Exception as e:
            logger.error(f"Error calculating strategy weight: {str(e)}")
            raise 