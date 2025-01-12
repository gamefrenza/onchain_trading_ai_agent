from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from src.utils.error_handler import (
    ErrorHandler,
    TradingError,
    NetworkError,
    ContractError
)
from src.utils.logger import get_logger
from src.trading.strategy_manager import StrategyManager
from src.models.trading_model import TradingModel

logger = get_logger()

class TradingService:
    def __init__(
        self,
        strategy_manager: StrategyManager,
        model: TradingModel,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.strategy_manager = strategy_manager
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.error_handler = ErrorHandler()
        
    async def execute_trade(
        self,
        trade_params: Dict[str, Any],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Execute trade with error handling and retries."""
        try:
            # Validate parameters
            self.error_handler.validate_trading_parameters(
                trade_params['symbol'],
                trade_params['amount'],
                trade_params['price']
            )
            
            # Get model prediction
            prediction = await self.get_prediction(trade_params['symbol'])
            self.error_handler.validate_model_prediction(prediction)
            
            # Execute strategy
            strategy_decision = await self.strategy_manager.execute_strategies({
                **trade_params,
                'prediction': prediction
            })
            
            if not strategy_decision:
                raise ValidationError(
                    message="Strategy validation failed",
                    error_code="VALIDATION_ERROR"
                )
            
            # Execute on-chain transaction
            return await self._execute_transaction(trade_params, strategy_decision)
            
        except NetworkError as e:
            if retry_count < self.max_retries:
                logger.warning(f"Retrying trade execution ({retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
                return await self.execute_trade(trade_params, retry_count + 1)
            raise
        except TradingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in trade execution: {str(e)}")
            raise
    
    @ErrorHandler.handle_contract_interaction
    async def _execute_transaction(
        self,
        trade_params: Dict[str, Any],
        strategy_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute blockchain transaction with error handling."""
        try:
            # Implement transaction logic here
            return {
                "status": "success",
                "transaction_hash": "0x...",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Transaction execution error: {str(e)}")
            raise
    
    async def get_prediction(self, symbol: str) -> np.ndarray:
        """Get model prediction with error handling."""
        try:
            # Get market data
            market_data = await self._fetch_market_data(symbol)
            
            # Make prediction
            prediction = self.model.predict(market_data['features'])
            
            return prediction
        except Exception as e:
            logger.error(f"Error getting prediction: {str(e)}")
            raise ModelError(
                message="Failed to get model prediction",
                error_code="MODEL_ERROR",
                details={"error": str(e)}
            )
    
    async def _fetch_market_data(
        self,
        symbol: str,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Fetch market data with retry mechanism."""
        try:
            # Implement market data fetching logic
            return {
                "features": np.random.random((1, 20)),
                "timestamp": datetime.utcnow().isoformat()
            }
        except ClientError as e:
            if retry_count < self.max_retries:
                logger.warning(f"Retrying market data fetch ({retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
                return await self._fetch_market_data(symbol, retry_count + 1)
            raise NetworkError(
                message="Failed to fetch market data",
                error_code="NETWORK_ERROR",
                details={"error": str(e)}
            ) 