from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Dict, List, Any
import asyncio

class Web3Client:
    def __init__(self, settings):
        self.w3 = Web3(Web3.WebsocketProvider(settings.WS_PROVIDER_URI))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.contracts: Dict[str, Any] = {}
        self.event_filters: Dict[str, Any] = {}
        
    async def setup_contract_monitoring(self, contract_addresses: List[str], abi: List[Dict]):
        """Setup monitoring for multiple DEX contracts"""
        for address in contract_addresses:
            contract = self.w3.eth.contract(address=address, abi=abi)
            self.contracts[address] = contract
            # Setup event filters
            self.event_filters[address] = contract.events.Swap.create_filter(fromBlock='latest')
            
    async def monitor_trading_events(self):
        """Monitor trading events from all contracts"""
        while True:
            try:
                for address, event_filter in self.event_filters.items():
                    events = event_filter.get_new_entries()
                    for event in events:
                        await self.process_trade_event(event)
            except Exception as e:
                logger.error(f"Error monitoring events: {str(e)}")
                await asyncio.sleep(5)  # Retry delay 