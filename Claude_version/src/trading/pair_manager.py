from typing import Dict, List
from dataclasses import dataclass

@dataclass
class TradingPair:
    address: str
    token0: str
    token1: str
    decimals0: int
    decimals1: int

class PairManager:
    def __init__(self):
        self.pairs: Dict[str, TradingPair] = {}
        self.active_pairs: List[str] = []
        
    async def add_pair(self, pair: TradingPair):
        """Add new trading pair for monitoring"""
        self.pairs[pair.address] = pair
        if pair.address not in self.active_pairs:
            self.active_pairs.append(pair.address)
            
    async def get_pair_info(self, address: str) -> TradingPair:
        """Get trading pair information"""
        return self.pairs.get(address) 