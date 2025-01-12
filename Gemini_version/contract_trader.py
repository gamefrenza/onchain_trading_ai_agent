from web3 import Web3
from eth_account import Account
import json
import os
from dotenv import load_dotenv
import logging
from decimal import Decimal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='contract_trading.log'
)

class ContractTrader:
    def __init__(self):
        """
        Initialize Web3 connection and load contract details
        """
        try:
            # Load environment variables
            load_dotenv()
            
            # Initialize Web3 connection
            self.w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_NODE_URL')))
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to Ethereum network")
            
            # Load contract ABI and address
            self.contract_address = os.getenv('TRADING_CONTRACT_ADDRESS')
            with open('contract_abi.json', 'r') as f:
                self.contract_abi = json.load(f)
            
            # Initialize contract
            self.contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contract_address),
                abi=self.contract_abi
            )
            
            logging.info("Successfully initialized ContractTrader")
            
        except Exception as e:
            logging.error(f"Initialization error: {str(e)}")
            raise

    def _get_account(self):
        """
        Securely retrieve account from environment or hardware wallet
        """
        try:
            # IMPORTANT: In production, use a secure key management solution
            # Options include:
            # 1. Hardware wallets (e.g., Ledger, Trezor)
            # 2. Key management services (e.g., AWS KMS)
            # 3. Secure encrypted storage
            
            # This is for demonstration only - NEVER store private keys in code or env variables
            private_key = os.getenv('TRADER_PRIVATE_KEY')
            if not private_key:
                raise ValueError("Trading account private key not found")
            
            account = Account.from_key(private_key)
            return account
            
        except Exception as e:
            logging.error(f"Error retrieving account: {str(e)}")
            raise

    def _estimate_gas(self, transaction):
        """
        Estimate gas for a transaction with safety margin
        """
        try:
            estimated_gas = self.w3.eth.estimate_gas(transaction)
            # Add 20% safety margin
            return int(estimated_gas * 1.2)
            
        except Exception as e:
            logging.error(f"Gas estimation error: {str(e)}")
            raise

    def _get_transaction_params(self, from_address, value=0):
        """
        Get current transaction parameters
        """
        try:
            return {
                'from': from_address,
                'nonce': self.w3.eth.get_transaction_count(from_address),
                'gas': 0,  # Will be estimated
                'gasPrice': self.w3.eth.gas_price,
                'value': value
            }
            
        except Exception as e:
            logging.error(f"Error getting transaction parameters: {str(e)}")
            raise

    def execute_trade(self, action, token_address, amount, max_slippage=0.01):
        """
        Execute a trade on the smart contract
        
        Parameters:
        action (str): 'buy' or 'sell'
        token_address (str): Address of token to trade
        amount (Decimal): Amount to trade
        max_slippage (float): Maximum acceptable slippage (default 1%)
        """
        try:
            # Get trading account
            account = self._get_account()
            
            # Convert amount to Wei
            amount_wei = self.w3.to_wei(amount, 'ether')
            
            # Prepare transaction parameters
            tx_params = self._get_transaction_params(account.address)
            
            # Prepare contract function based on action
            if action.lower() == 'buy':
                contract_function = self.contract.functions.buy(
                    self.w3.to_checksum_address(token_address),
                    amount_wei,
                    int(max_slippage * 10000)  # Convert to basis points
                )
            elif action.lower() == 'sell':
                contract_function = self.contract.functions.sell(
                    self.w3.to_checksum_address(token_address),
                    amount_wei,
                    int(max_slippage * 10000)  # Convert to basis points
                )
            else:
                raise ValueError("Invalid action. Must be 'buy' or 'sell'")
            
            # Build transaction
            transaction = contract_function.build_transaction(tx_params)
            
            # Estimate gas
            transaction['gas'] = self._estimate_gas(transaction)
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, account.key
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logging.info(f"Transaction sent: {tx_hash.hex()}")
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Check transaction status
            if tx_receipt['status'] == 1:
                logging.info(f"Transaction successful: {tx_receipt['transactionHash'].hex()}")
            else:
                raise Exception("Transaction failed")
            
            return tx_receipt
            
        except Exception as e:
            logging.error(f"Trade execution error: {str(e)}")
            raise

    def check_allowance(self, token_address, owner_address):
        """
        Check token allowance for trading contract
        """
        try:
            # Load ERC20 ABI - This is a minimal ABI for allowance checking
            erc20_abi = json.loads('''[
                {
                    "constant": true,
                    "inputs": [
                        {"name": "owner", "type": "address"},
                        {"name": "spender", "type": "address"}
                    ],
                    "name": "allowance",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function"
                }
            ]''')
            
            token_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(token_address),
                abi=erc20_abi
            )
            
            allowance = token_contract.functions.allowance(
                self.w3.to_checksum_address(owner_address),
                self.contract_address
            ).call()
            
            return allowance
            
        except Exception as e:
            logging.error(f"Error checking allowance: {str(e)}")
            raise


def main():
    """
    Example usage of ContractTrader
    """
    try:
        trader = ContractTrader()
        
        # Example token address (e.g., USDC on Ethereum mainnet)
        token_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        
        # Check allowance before trading
        account = trader._get_account()
        allowance = trader.check_allowance(token_address, account.address)
        print(f"Current allowance: {allowance}")
        
        # Execute trade if sufficient allowance
        if allowance > 0:
            receipt = trader.execute_trade(
                action='buy',
                token_address=token_address,
                amount=Decimal('0.1'),  # Trade 0.1 ETH worth
                max_slippage=0.01  # 1% max slippage
            )
            print(f"Trade executed: {receipt['transactionHash'].hex()}")
        
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 