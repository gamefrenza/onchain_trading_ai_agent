from typing import Dict, Any, Optional, Callable
from fastapi import HTTPException
from web3.exceptions import (
    ContractLogicError,
    ValidationError,
    TimeExhausted,
    BadFunctionCallOutput
)
from aiohttp import ClientTimeout, ClientError
import numpy as np
from src.utils.logger import get_logger
from functools import wraps
import asyncio

logger = get_logger()

class TradingError(Exception):
    """Base exception for trading-related errors."""
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class NetworkError(TradingError):
    """Network-related errors."""
    pass

class ContractError(TradingError):
    """Smart contract interaction errors."""
    pass

class ValidationError(TradingError):
    """Data validation errors."""
    pass

class ModelError(TradingError):
    """ML model-related errors."""
    pass

class ErrorHandler:
    # HTTP status codes mapping
    STATUS_CODES = {
        'NETWORK_ERROR': 503,
        'CONTRACT_ERROR': 502,
        'VALIDATION_ERROR': 400,
        'MODEL_ERROR': 500,
        'TIMEOUT_ERROR': 504
    }
    
    @staticmethod
    async def handle_contract_interaction(func):
        """Decorator for handling smart contract interactions."""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ContractLogicError as e:
                logger.error(f"Contract logic error: {str(e)}")
                raise ContractError(
                    message="Smart contract execution failed",
                    error_code="CONTRACT_ERROR",
                    details={"original_error": str(e)}
                )
            except TimeExhausted as e:
                logger.error(f"Contract transaction timeout: {str(e)}")
                raise NetworkError(
                    message="Transaction timed out",
                    error_code="TIMEOUT_ERROR",
                    details={"timeout": str(e)}
                )
            except Exception as e:
                logger.error(f"Unexpected contract error: {str(e)}")
                raise
        return wrapper
    
    @staticmethod
    def validate_trading_parameters(
        symbol: str,
        amount: float,
        price: float,
        max_slippage: float = 0.02
    ) -> None:
        """Validate trading parameters."""
        try:
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise ValidationError(
                    message="Invalid trade amount",
                    error_code="VALIDATION_ERROR",
                    details={"amount": amount}
                )
            
            if not isinstance(price, (int, float)) or price <= 0:
                raise ValidationError(
                    message="Invalid price",
                    error_code="VALIDATION_ERROR",
                    details={"price": price}
                )
            
            if max_slippage < 0 or max_slippage > 0.1:
                raise ValidationError(
                    message="Invalid slippage parameter",
                    error_code="VALIDATION_ERROR",
                    details={"max_slippage": max_slippage}
                )
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected validation error: {str(e)}")
            raise
    
    @staticmethod
    def validate_model_prediction(
        prediction: np.ndarray,
        confidence_threshold: float = 0.6
    ) -> None:
        """Validate model predictions."""
        try:
            if prediction is None or not isinstance(prediction, np.ndarray):
                raise ModelError(
                    message="Invalid prediction format",
                    error_code="MODEL_ERROR",
                    details={"prediction_type": type(prediction)}
                )
            
            if np.isnan(prediction).any():
                raise ModelError(
                    message="Prediction contains NaN values",
                    error_code="MODEL_ERROR"
                )
            
            if np.abs(prediction).max() > 1.0:
                raise ModelError(
                    message="Prediction values out of expected range",
                    error_code="MODEL_ERROR",
                    details={"max_value": float(np.abs(prediction).max())}
                )
                
        except ModelError:
            raise
        except Exception as e:
            logger.error(f"Unexpected model validation error: {str(e)}")
            raise
    
    @staticmethod
    def handle_api_error(error: Exception) -> HTTPException:
        """Convert internal errors to FastAPI HTTP exceptions."""
        if isinstance(error, TradingError):
            status_code = ErrorHandler.STATUS_CODES.get(error.error_code, 500)
            return HTTPException(
                status_code=status_code,
                detail={
                    "message": error.message,
                    "error_code": error.error_code,
                    "details": error.details
                }
            )
        
        return HTTPException(
            status_code=500,
            detail={
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "details": {"error": str(error)}
            }
        ) 

class RetryableError(Exception):
    pass

def with_retry(max_retries: int = 3, delay: int = 1):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except RetryableError as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"Max retries reached for {func.__name__}: {str(e)}")
                        raise
                    logger.warning(f"Retry {retries}/{max_retries} for {func.__name__}")
                    await asyncio.sleep(delay * retries)
            return None
        return wrapper
    return decorator 