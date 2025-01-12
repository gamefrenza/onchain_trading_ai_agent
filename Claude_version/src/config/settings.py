from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings(BaseSettings):
    # Blockchain settings
    WEB3_PROVIDER_URI: str
    WALLET_ADDRESS: str
    PRIVATE_KEY: str
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Model settings
    MODEL_PATH: str = "models/trained_model"
    
    # Event listener settings
    POLLING_INTERVAL: float = 1.0  # seconds
    ERROR_RETRY_DELAY: int = 5  # seconds
    WS_PROVIDER_URI: str
    
    # DEX contract addresses
    UNISWAP_V2_ROUTER: str = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    SUSHISWAP_ROUTER: str = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    
    # Trading pairs to monitor
    TRADING_PAIRS: List[str] = [
        "WETH/USDC",
        "WETH/USDT",
        "WBTC/USDT"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings() 