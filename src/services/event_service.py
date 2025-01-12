from typing import Dict, Any
import asyncio
from web3 import Web3, WebsocketProvider
from src.blockchain.event_listener import EventListener
from src.config.settings import settings
from src.utils.logger import get_logger
from src.database.models import TradeEvent  # You'll need to implement this

logger = get_logger()

class EventService:
    def __init__(self):
        self.w3 = Web3(WebsocketProvider(settings.WS_PROVIDER_URI))
        self.event_listener = EventListener(self.w3)
        self.running = False
        
    async def initialize(self):
        """Initialize contracts and event filters."""
        try:
            # Add Uniswap contract
            await self.event_listener.add_contract(
                address=settings.UNISWAP_V2_ROUTER,
                abi=UNISWAP_V2_ABI,  # You'll need to provide this
                name="uniswap_v2"
            )
            
            # Add SushiSwap contract
            await self.event_listener.add_contract(
                address=settings.SUSHISWAP_ROUTER,
                abi=SUSHISWAP_ABI,  # You'll need to provide this
                name="sushiswap"
            )
            
            # Setup event filters for each DEX
            for dex in ["uniswap_v2", "sushiswap"]:
                await self.event_listener.setup_event_filter(
                    contract_name=dex,
                    event_name="Swap"
                )
                
            logger.info("Initialized event service")
        except Exception as e:
            logger.error(f"Error initializing event service: {str(e)}")
            raise

    async def process_trade_event(self, event: Dict[str, Any]):
        """Process and store trade events."""
        try:
            # Create trade event record
            trade_event = TradeEvent(
                transaction_hash=event['transaction_hash'],
                block_number=event['block_number'],
                timestamp=event['timestamp'],
                dex_address=event['address'],
                event_type=event['event_type'],
                token_in=event['args'].get('tokenIn'),
                token_out=event['args'].get('tokenOut'),
                amount_in=event['args'].get('amountIn'),
                amount_out=event['args'].get('amountOut')
            )
            
            # Save to database (implement this part)
            await trade_event.save()
            
            # Emit WebSocket update
            await self.broadcast_event(event)
            
        except Exception as e:
            logger.error(f"Error processing trade event: {str(e)}")
            raise

    async def broadcast_event(self, event: Dict[str, Any]):
        """Broadcast event to WebSocket clients."""
        # Implement WebSocket broadcasting logic here
        pass

    async def start(self):
        """Start the event listening service."""
        if self.running:
            return
            
        self.running = True
        try:
            await self.initialize()
            await self.event_listener.listen_to_events(self.process_trade_event)
        except Exception as e:
            self.running = False
            logger.error(f"Error in event service: {str(e)}")
            raise
        finally:
            self.running = False

    async def stop(self):
        """Stop the event listening service."""
        self.running = False 