from web3 import Web3
from typing import Dict, List, Optional, Union
import os
import json
from dotenv import load_dotenv
import ccxt
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

class BlockchainDataFetcher:
    def __init__(self):
        # Initialize blockchain connections
        self.eth_node = Web3(Web3.HTTPProvider(os.getenv('ETH_NODE_URL', 'https://mainnet.infura.io/v3/YOUR-PROJECT-ID')))
        self.binance_client = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_SECRET_KEY')
        })
        
        # Standard ABI for ERC20 token events
        self.erc20_abi = json.loads('''[
            {"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},
             {"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],
             "name":"Transfer","type":"event"}
        ]''')

    async def get_latest_eth_transactions(self, num_blocks: int = 1) -> List[Dict]:
        """Fetch latest Ethereum transactions"""
        try:
            latest_block = self.eth_node.eth.block_number
            transactions = []
            
            for block_number in range(latest_block - num_blocks + 1, latest_block + 1):
                block = self.eth_node.eth.get_block(block_number, full_transactions=True)
                for tx in block.transactions:
                    transactions.append({
                        'hash': tx['hash'].hex(),
                        'from': tx['from'],
                        'to': tx['to'],
                        'value': self.eth_node.from_wei(tx['value'], 'ether'),
                        'block_number': block_number,
                        'timestamp': datetime.fromtimestamp(block['timestamp']).isoformat()
                    })
            return transactions
        except Exception as e:
            print(f"Error fetching ETH transactions: {str(e)}")
            return []

    async def get_token_transfers(self, token_address: str, from_block: int = None) -> List[Dict]:
        """Fetch ERC20 token transfer events"""
        try:
            contract = self.eth_node.eth.contract(
                address=self.eth_node.to_checksum_address(token_address),
                abi=self.erc20_abi
            )
            
            if from_block is None:
                from_block = self.eth_node.eth.block_number - 100

            transfer_filter = contract.events.Transfer.create_filter(
                fromBlock=from_block
            )
            
            events = transfer_filter.get_all_entries()
            return [{
                'from': event['args']['from'],
                'to': event['args']['to'],
                'value': event['args']['value'],
                'transaction_hash': event['transactionHash'].hex(),
                'block_number': event['blockNumber'],
                'timestamp': datetime.fromtimestamp(
                    self.eth_node.eth.get_block(event['blockNumber'])['timestamp']
                ).isoformat()
            } for event in events]
        except Exception as e:
            print(f"Error fetching token transfers: {str(e)}")
            return []

    async def get_dex_trades(self, pair: str = 'ETH/USDT', limit: int = 100) -> List[Dict]:
        """Fetch recent DEX trades"""
        try:
            trades = self.binance_client.fetch_trades(pair, limit=limit)
            return [{
                'symbol': trade['symbol'],
                'price': trade['price'],
                'amount': trade['amount'],
                'side': trade['side'],
                'timestamp': datetime.fromtimestamp(trade['timestamp']/1000).isoformat()
            } for trade in trades]
        except Exception as e:
            print(f"Error fetching DEX trades: {str(e)}")
            return []

    async def monitor_mempool(self, callback):
        """Monitor mempool for pending transactions"""
        try:
            async def handle_pending(pending_tx):
                tx = self.eth_node.eth.get_transaction(pending_tx)
                if tx:
                    await callback({
                        'hash': tx['hash'].hex(),
                        'from': tx['from'],
                        'to': tx['to'],
                        'value': self.eth_node.from_wei(tx['value'], 'ether'),
                        'gas_price': self.eth_node.from_wei(tx['gasPrice'], 'gwei')
                    })

            pending_filter = self.eth_node.eth.filter('pending')
            while True:
                for tx_hash in pending_filter.get_new_entries():
                    await handle_pending(tx_hash)
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error monitoring mempool: {str(e)}") 