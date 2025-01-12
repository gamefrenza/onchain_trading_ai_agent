from web3 import Web3, AsyncWeb3
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger()

class Web3Client:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))
        self.async_w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.WEB3_PROVIDER_URI))
        self.address = settings.WALLET_ADDRESS
        
    async def get_eth_balance(self) -> float:
        try:
            balance = await self.async_w3.eth.get_balance(self.address)
            return self.w3.from_wei(balance, 'ether')
        except Exception as e:
            logger.error(f"Error getting ETH balance: {str(e)}")
            raise
            
    async def send_transaction(self, to_address: str, amount: float):
        try:
            transaction = {
                'to': to_address,
                'value': self.w3.to_wei(amount, 'ether'),
                'gas': 21000,
                'gasPrice': await self.async_w3.eth.gas_price,
                'nonce': await self.async_w3.eth.get_transaction_count(self.address),
            }
            
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, settings.PRIVATE_KEY
            )
            tx_hash = await self.async_w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"Error sending transaction: {str(e)}")
            raise 