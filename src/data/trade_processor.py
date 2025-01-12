from datetime import datetime
from typing import Dict, Any
from src.models.trade import Trade
from src.utils.logger import get_logger

logger = get_logger()

class TradeProcessor:
    def __init__(self, db_session):
        self.db_session = db_session
        
    async def process_trade_event(self, event: Dict[str, Any]) -> Trade:
        """Process and store trade event data"""
        try:
            trade = Trade(
                transaction_hash=event.transactionHash.hex(),
                pair_address=event.address,
                token0_amount=event.args.amount0In or event.args.amount0Out,
                token1_amount=event.args.amount1In or event.args.amount1Out,
                timestamp=datetime.utcnow(),
                block_number=event.blockNumber,
                sender=event.args.sender
            )
            
            await self.db_session.add(trade)
            await self.db_session.commit()
            return trade
            
        except Exception as e:
            logger.error(f"Error processing trade: {str(e)}")
            await self.db_session.rollback()
            raise 