from dataclasses import dataclass
from typing import List, Dict, Any
import asyncio
from asyncio import timeout
import logging

logger = logging.getLogger(__name__)

@dataclass
class RiskRule:
    name: str
    condition: callable
    action: callable
    priority: int

class RiskRuleEngine:
    def __init__(self):
        self.rules: List[RiskRule] = []
        self._lock = asyncio.Lock()
        
    def _setup_default_rules(self):
        """Setup default risk management rules"""
        self.rules.extend([
            RiskRule(
                name="max_position_size",
                condition=lambda data: data['position_size'] > data['max_allowed'],
                action=lambda data: {'position_size': data['max_allowed']},
                priority=1
            ),
            RiskRule(
                name="volatility_adjustment",
                condition=lambda data: data['volatility'] > data['volatility_threshold'],
                action=lambda data: {
                    'position_size': data['position_size'] * 0.8,
                    'stop_loss_pct': data['stop_loss_pct'] * 1.2
                },
                priority=2
            )
        ])
    
    async def apply_rules(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply risk rules with validation and safety checks"""
        try:
            # Validate input data
            if not isinstance(trade_data, dict):
                raise ValueError('Invalid trade data format')
                
            required_fields = {'position_size', 'price', 'timestamp'}
            if not all(field in trade_data for field in required_fields):
                raise ValueError('Missing required trade data fields')
                
            async with self._lock:
                modified_data = trade_data.copy()
                
                # Apply rules with timeout
                async with timeout(5):  # 5 second timeout
                    for rule in sorted(self.rules, key=lambda x: x.priority):
                        try:
                            if rule.condition(modified_data):
                                modifications = rule.action(modified_data)
                                modified_data.update(modifications)
                        except Exception as e:
                            logger.error(f"Rule {rule.name} failed: {str(e)}")
                            continue
                            
                return modified_data
                
        except Exception as e:
            logger.error(f"Error applying risk rules: {str(e)}")
            raise 