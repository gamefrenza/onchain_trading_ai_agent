from pydantic import BaseSettings

class ModelConfig(BaseSettings):
    MODEL_PATH: str
    BATCH_SIZE: int = 32
    SEQUENCE_LENGTH: int = 60
    FEATURE_COLUMNS: list = [
        'close', 'volume', 'rsi', 'macd',
        'macd_signal', 'bb_upper', 'bb_lower'
    ]
    
    # Model serving
    MAX_QUEUE_SIZE: int = 100
    PREDICTION_TIMEOUT: int = 30
    CACHE_TTL: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env" 