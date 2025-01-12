from typing import Dict, Optional, List
from web3 import Web3
from eth_typing import Address
from web3.contract import Contract
import json
import asyncio
from decimal import Decimal
from datetime import datetime
import logging
from trading_strategy import TradingStrategy, TradingSignal
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self, 
                 web3_provider: str,
                 private_key: str,
                 dex_router_address: str,
                 max_slippage: float = 0.005):  # 0.5% default slippage
        """
        Initialize trade executor with blockchain connection details
        
        Args:
            web3_provider: Ethereum node URL
            private_key: Private key for transaction signing
            dex_router_address: DEX router contract address
            max_slippage: Maximum allowed slippage percentage
        """
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.account = self.w3.eth.account.from_key(private_key)
        self.max_slippage = max_slippage
        
        # Load DEX router ABI (Example using Uniswap V2 Router)
        self.router_abi = json.loads('''[
            {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},
             {"internalType":"uint256","name":"amountOutMin","type":"uint256"},
             {"internalType":"address[]","name":"path","type":"address[]"},
             {"internalType":"address","name":"to","type":"address"},
             {"internalType":"uint256","name":"deadline","type":"uint256"}],
             "name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]",
             "name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},
             {"internalType":"address[]","name":"path","type":"address[]"}],
             "name":"getAmountsOut","outputs":[{"internalType":"uint256[]",
             "name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}
        ]''')
        
        self.router_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(dex_router_address),
            abi=self.router_abi
        )
        
        # Transaction tracking
        self.pending_transactions: Dict[str, Dict] = {}
        self.executed_trades: List[Dict] = []
        
    async def execute_signal(self, signal: TradingSignal, token_addresses: Dict[str, str]) -> Optional[str]:
        """Execute a trading signal on the DEX"""
        try:
            # Prepare token addresses
            token_in = self.w3.to_checksum_address(token_addresses['in'])
            token_out = self.w3.to_checksum_address(token_addresses['out'])
            
            # Get token contracts
            token_in_contract = self._get_erc20_contract(token_in)
            
            # Calculate amounts
            amount_in = self._calculate_trade_amount(signal)
            
            # Check allowance and approve if needed
            await self._ensure_token_approval(token_in_contract, amount_in)
            
            # Get expected output amount
            amounts = self.router_contract.functions.getAmountsOut(
                amount_in,
                [token_in, token_out]
            ).call()
            
            expected_out = amounts[1]
            min_out = int(expected_out * (1 - self.max_slippage))
            
            # Prepare transaction
            deadline = self.w3.eth.get_block('latest')['timestamp'] + 300  # 5 minutes
            
            # Build transaction
            transaction = self.router_contract.functions.swapExactTokensForTokens(
                amount_in,
                min_out,
                [token_in, token_out],
                self.account.address,
                deadline
            ).build_transaction({
                'from': self.account.address,
                'gas': 250000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # Sign and send transaction
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Track pending transaction
            self.pending_transactions[tx_hash.hex()] = {
                'signal': signal,
                'amount_in': amount_in,
                'expected_out': expected_out,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            return None
            
    async def monitor_transactions(self):
        """Monitor pending transactions and update their status"""
        while True:
            try:
                for tx_hash in list(self.pending_transactions.keys()):
                    receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                    if receipt:
                        if receipt['status'] == 1:
                            trade_info = self.pending_transactions[tx_hash]
                            self.executed_trades.append({
                                'tx_hash': tx_hash,
                                'signal': trade_info['signal'],
                                'amount_in': trade_info['amount_in'],
                                'expected_out': trade_info['expected_out'],
                                'gas_used': receipt['gasUsed'],
                                'timestamp': trade_info['timestamp']
                            })
                            logger.info(f"Transaction confirmed: {tx_hash}")
                        else:
                            logger.error(f"Transaction failed: {tx_hash}")
                            
                        del self.pending_transactions[tx_hash]
                        
            except Exception as e:
                logger.error(f"Error monitoring transactions: {str(e)}")
                
            await asyncio.sleep(1)
            
    def _get_erc20_contract(self, token_address: str) -> Contract:
        """Get ERC20 token contract instance"""
        abi = json.loads('''[
            {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
            {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf",
             "outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
            {"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],
             "name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"},
            {"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],
             "name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"}
        ]''')
        
        return self.w3.eth.contract(address=token_address, abi=abi)
    
    async def _ensure_token_approval(self, token_contract: Contract, amount: int):
        """Ensure DEX router has approval to spend tokens"""
        current_allowance = token_contract.functions.allowance(
            self.account.address,
            self.router_contract.address
        ).call()
        
        if current_allowance < amount:
            approve_txn = token_contract.functions.approve(
                self.router_contract.address,
                amount
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            signed_txn = self.account.sign_transaction(approve_txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for approval transaction to be mined
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt['status'] != 1:
                raise Exception("Token approval failed")
    
    def _calculate_trade_amount(self, signal: TradingSignal) -> int:
        """Calculate the exact amount of tokens to trade"""
        # This should be implemented based on your position sizing logic
        # For now, using a simple fixed amount
        return int(signal.position_size * 10**18)  # Assuming 18 decimals 