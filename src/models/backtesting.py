from typing import Dict, List
import pandas as pd
import numpy as np

class Backtester:
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.positions: Dict[str, float] = {}
        self.trades: List[Dict] = []
        
    def run_backtest(
        self,
        predictions: np.ndarray,
        actual_prices: np.ndarray,
        transaction_costs: float = 0.001
    ) -> Dict[str, float]:
        """Run backtest simulation"""
        portfolio_value = self.initial_capital
        position = 0
        
        for i in range(len(predictions)):
            # Generate trading signal
            signal = self._generate_signal(predictions[i])
            
            # Execute trade
            if signal != position:
                # Calculate transaction cost
                cost = abs(signal - position) * actual_prices[i] * transaction_costs
                portfolio_value -= cost
                
                # Update position
                position = signal
                self.trades.append({
                    'timestamp': i,
                    'price': actual_prices[i],
                    'position': position,
                    'portfolio_value': portfolio_value
                })
        
        return self._calculate_metrics() 