import time
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import psutil
import logging
from typing import Dict, Any, List
import threading
from datetime import datetime
from functools import wraps

class SystemMonitor:
    def __init__(self, port: int = 9090, max_history: int = 1000):
        # Initialize Prometheus metrics
        self.trades_counter = Counter('ai_trading_trades_total', 
                                    'Total number of trades executed',
                                    ['type', 'status'])
        
        self.position_gauge = Gauge('ai_trading_positions', 
                                  'Current number of open positions')
        
        self.capital_gauge = Gauge('ai_trading_capital', 
                                 'Current trading capital')
        
        self.profit_gauge = Gauge('ai_trading_profit', 
                                'Current profit/loss')
        
        self.signal_latency = Histogram('ai_trading_signal_latency_seconds',
                                      'Time taken to generate trading signals',
                                      buckets=[0.1, 0.5, 1.0, 2.0, 5.0])
        
        self.execution_latency = Histogram('ai_trading_execution_latency_seconds',
                                         'Time taken to execute trades',
                                         buckets=[0.1, 0.5, 1.0, 2.0, 5.0])
        
        self.system_metrics = {
            'cpu_usage': Gauge('ai_trading_cpu_usage_percent', 
                             'CPU usage percentage'),
            'memory_usage': Gauge('ai_trading_memory_usage_bytes', 
                                'Memory usage in bytes'),
            'disk_usage': Gauge('ai_trading_disk_usage_percent', 
                              'Disk usage percentage')
        }
        
        # Start Prometheus HTTP server
        start_http_server(port)
        
        # Start system metrics collection
        self.start_system_metrics_collection()
        
        # Add max history limit
        self.max_history = max_history
        
    def record_trade(self, trade_type: str, status: str):
        """Record a trade execution"""
        self.trades_counter.labels(type=trade_type, status=status).inc()
        
    def update_positions(self, num_positions: int):
        """Update number of open positions"""
        self.position_gauge.set(num_positions)
        
    def update_capital(self, capital: float):
        """Update current trading capital"""
        self.capital_gauge.set(capital)
        
    def update_profit(self, profit: float):
        """Update current profit/loss"""
        self.profit_gauge.set(profit)
        
    def measure_signal_latency(self):
        """Context manager to measure signal generation latency"""
        return self.signal_latency.time()
        
    def measure_execution_latency(self):
        """Context manager to measure trade execution latency"""
        return self.execution_latency.time()
        
    def collect_system_metrics(self):
        """Collect system metrics with error handling"""
        while True:
            try:
                # Add timeout
                with timeout(5):
                    self._collect_metrics()
            except TimeoutError:
                logger.error("Metrics collection timeout")
            except Exception as e:
                logger.error(f"Metrics error: {str(e)}")
            finally:
                # Ensure cleanup
                self._cleanup_old_metrics()
        
    def start_system_metrics_collection(self):
        """Start system metrics collection in background thread"""
        thread = threading.Thread(target=self.collect_system_metrics, daemon=True)
        thread.start()

class PerformanceMonitor:
    def __init__(self):
        self.trade_history: List[Dict[str, Any]] = []
        self.performance_metrics = {
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0
        }
        
    def record_trade(self, trade_data: Dict[str, Any]):
        """Record trade details for performance analysis"""
        self.trade_history.append({
            **trade_data,
            'timestamp': datetime.now()
        })
        self.update_metrics()
        
    def update_metrics(self):
        """Update performance metrics"""
        if not self.trade_history:
            return
            
        # Calculate win rate
        profitable_trades = sum(1 for trade in self.trade_history 
                              if trade['pnl'] > 0)
        self.performance_metrics['win_rate'] = (
            profitable_trades / len(self.trade_history)
        )
        
        # Calculate average profit
        total_pnl = sum(trade['pnl'] for trade in self.trade_history)
        self.performance_metrics['avg_profit'] = (
            total_pnl / len(self.trade_history)
        )
        
        # Calculate maximum drawdown
        cumulative_pnl = 0
        peak = 0
        max_drawdown = 0
        
        for trade in self.trade_history:
            cumulative_pnl += trade['pnl']
            peak = max(peak, cumulative_pnl)
            drawdown = peak - cumulative_pnl
            max_drawdown = max(max_drawdown, drawdown)
            
        self.performance_metrics['max_drawdown'] = max_drawdown
        
        # Calculate Sharpe ratio (simplified)
        returns = [trade['pnl'] for trade in self.trade_history]
        if len(returns) > 1:
            avg_return = sum(returns) / len(returns)
            std_dev = (sum((r - avg_return) ** 2 for r in returns) 
                      / (len(returns) - 1)) ** 0.5
            if std_dev > 0:
                self.performance_metrics['sharpe_ratio'] = (
                    avg_return / std_dev * (252 ** 0.5)  # Annualized
                ) 