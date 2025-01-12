from typing import List, Dict, Any
import pandas as pd
import numpy as np
from src.utils.logger import get_logger
from src.models.risk_management import RiskManager

logger = get_logger()

class Backtester:
    def __init__(
        self,
        initial_capital: float = 100000.0,
        transaction_fee: float = 0.001
    ):
        self.initial_capital = initial_capital
        self.transaction_fee = transaction_fee
        self.risk_manager = RiskManager()
        
    def run_backtest(
        self,
        predictions: np.ndarray,
        actual_prices: np.ndarray,
        dates: pd.DatetimeIndex
    ) -> Dict[str, Any]:
        """Run backtest simulation."""
        try:
            portfolio_value = self.initial_capital
            positions: List[Dict[str, Any]] = []
            trades: List[Dict[str, Any]] = []
            
            for i in range(1, len(predictions)):
                # Apply risk management
                safe_prediction = self.risk_manager.apply_risk_rules(
                    predictions[i].reshape(1, -1)
                )[0]
                
                # Determine action based on prediction
                if safe_prediction > 0.02:  # Buy signal
                    if self.risk_manager.validate_trade({}, portfolio_value):
                        position_size = self.risk_manager.calculate_position_size(
                            safe_prediction,
                            0.8,  # Confidence score
                            portfolio_value
                        )
                        
                        # Execute trade
                        shares = position_size / actual_prices[i]
                        cost = shares * actual_prices[i] * (1 + self.transaction_fee)
                        
                        if cost <= portfolio_value:
                            portfolio_value -= cost
                            positions.append({
                                'entry_price': actual_prices[i],
                                'shares': shares,
                                'entry_date': dates[i],
                                'stop_loss': self.risk_manager.calculate_stop_loss(actual_prices[i])
                            })
                            
                            trades.append({
                                'type': 'buy',
                                'date': dates[i],
                                'price': actual_prices[i],
                                'shares': shares,
                                'value': cost
                            })
                
                # Check stop losses and take profits
                for position in positions[:]:
                    if actual_prices[i] <= position['stop_loss']:
                        # Stop loss hit
                        value = position['shares'] * actual_prices[i] * (1 - self.transaction_fee)
                        portfolio_value += value
                        
                        trades.append({
                            'type': 'sell',
                            'date': dates[i],
                            'price': actual_prices[i],
                            'shares': position['shares'],
                            'value': value,
                            'reason': 'stop_loss'
                        })
                        
                        positions.remove(position)
            
            return self.calculate_performance_metrics(trades, dates)
        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            raise
            
    def calculate_performance_metrics(
        self,
        trades: List[Dict[str, Any]],
        dates: pd.DatetimeIndex
    ) -> Dict[str, Any]:
        """Calculate performance metrics from backtest results."""
        try:
            df_trades = pd.DataFrame(trades)
            
            # Calculate returns
            returns = []
            for buy, sell in zip(
                df_trades[df_trades['type'] == 'buy'].iterrows(),
                df_trades[df_trades['type'] == 'sell'].iterrows()
            ):
                returns.append((sell[1]['value'] - buy[1]['value']) / buy[1]['value'])
            
            return {
                'total_trades': len(trades),
                'winning_trades': sum(r > 0 for r in returns),
                'average_return': np.mean(returns) if returns else 0,
                'sharpe_ratio': self.calculate_sharpe_ratio(returns),
                'max_drawdown': self.calculate_max_drawdown(returns),
                'final_value': sum(t['value'] for t in trades if t['type'] == 'sell')
            }
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            raise
            
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.01) -> float:
        """Calculate Sharpe ratio."""
        if not returns:
            return 0
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate
        return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0
        
    @staticmethod
    def calculate_max_drawdown(returns: List[float]) -> float:
        """Calculate maximum drawdown."""
        if not returns:
            return 0
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = cumulative / running_max - 1
        return np.min(drawdowns) 