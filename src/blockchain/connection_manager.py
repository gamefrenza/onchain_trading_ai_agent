from web3 import Web3
from src.utils.error_handler import with_retry, RetryableError

class ConnectionManager:
    def __init__(self, urls: List[str]):
        self.provider_urls = urls
        self.current_provider = 0
        
    @with_retry(max_retries=3, delay=2)
    async def get_web3_connection(self) -> Web3:
        """Get Web3 connection with retry mechanism"""
        try:
            provider_url = self.provider_urls[self.current_provider]
            w3 = Web3(Web3.WebsocketProvider(provider_url))
            if not w3.is_connected():
                raise RetryableError("Failed to connect to provider")
            return w3
        except Exception as e:
            self.current_provider = (self.current_provider + 1) % len(self.provider_urls)
            raise RetryableError(f"Connection error: {str(e)}") 