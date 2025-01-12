from typing import Dict, List, Any
import pandas as pd
import numpy as np
import asyncio

class PerformanceTracker:
    def __init__(self):
        self.trades: List[Dict[str, Any]] = []
        self.metrics: Dict[str, float] = {}
        self._lock = asyncio.Lock()  # Add thread safety
        
    async def add_trade(self, trade: Dict[str, Any]):
        """Add trade to performance tracking with validation"""
        try:
            # Validate trade data
            required_fields = {'timestamp', 'price', 'amount', 'type'}
            if not all(field in trade for field in required_fields):
                raise ValueError('Missing required trade fields')
                
            async with self._lock:
                self.trades.append(trade)
                await self._update_metrics()
                
        except Exception as e:
            logger.error(f"Error adding trade: {str(e)}")
            raise 