from typing import List, Dict, Any, Optional
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import WebsocketConnectionError
from websockets.exceptions import ConnectionClosed
import asyncio
import json
from datetime import datetime
from src.utils.logger import get_logger
from src.config.settings import settings

logger = get_logger()

class EventListener:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.contracts: Dict[str, Contract] = {}
        self.event_filters: Dict[str, Any] = {}
        self.retry_count = 3
        self.retry_delay = 5  # seconds
        
    async def add_contract(self, address: str, abi: str, name: str) -> None:
        """Add a new contract to monitor."""
        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(address),
                abi=json.loads(abi)
            )
            self.contracts[name] = contract
            logger.info(f"Added contract {name} at {address}")
        except Exception as e:
            logger.error(f"Error adding contract {name}: {str(e)}")
            raise

    async def setup_event_filter(
        self,
        contract_name: str,
        event_name: str,
        from_block: Optional[int] = None
    ) -> None:
        """Setup event filter for a specific contract event."""
        try:
            contract = self.contracts[contract_name]
            event = getattr(contract.events, event_name)
            
            if from_block is None:
                from_block = await self.w3.eth.block_number
                
            event_filter = event.create_filter(fromBlock=from_block)
            filter_key = f"{contract_name}_{event_name}"
            self.event_filters[filter_key] = event_filter
            
            logger.info(f"Setup event filter for {filter_key}")
        except Exception as e:
            logger.error(f"Error setting up event filter: {str(e)}")
            raise

    async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single event and return structured data."""
        try:
            return {
                'transaction_hash': event.transactionHash.hex(),
                'block_number': event.blockNumber,
                'timestamp': datetime.utcnow().isoformat(),
                'address': event.address,
                'event_type': event.event,
                'args': dict(event.args),
                'processed': False
            }
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
            raise

    async def handle_event_with_retry(self, event_filter: Any) -> List[Dict[str, Any]]:
        """Get events from filter with retry mechanism."""
        for attempt in range(self.retry_count):
            try:
                events = event_filter.get_new_entries()
                return [await self.process_event(event) for event in events]
            except (WebsocketConnectionError, ConnectionClosed) as e:
                if attempt == self.retry_count - 1:
                    logger.error(f"Max retries reached: {str(e)}")
                    raise
                logger.warning(f"Connection error, retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"Unexpected error in handle_event_with_retry: {str(e)}")
                raise

    async def listen_to_events(self, callback) -> None:
        """Main event listening loop."""
        while True:
            try:
                for filter_key, event_filter in self.event_filters.items():
                    events = await self.handle_event_with_retry(event_filter)
                    if events:
                        for event in events:
                            await callback(event)
                            logger.info(f"Processed event from {filter_key}: {event['transaction_hash']}")
                
                await asyncio.sleep(settings.POLLING_INTERVAL)
            except Exception as e:
                logger.error(f"Error in event listening loop: {str(e)}")
                await asyncio.sleep(settings.ERROR_RETRY_DELAY) 