from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Dict, Any
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from src.utils.logger import get_logger
from src.trading.strategy_manager import StrategyManager
from src.models.trading_model import TradingModel
from src.config.settings import settings
from src.utils.error_handler import ErrorHandler, TradingError
from src.services.trading_service import TradingService
from src.services.health_check import (
    check_database_connection,
    check_model_status,
    check_websocket_status
)

logger = get_logger()
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class User(BaseModel):
    username: str
    email: str
    disabled: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class TradeRequest(BaseModel):
    symbol: str
    action: str
    amount: float
    strategy: str = None

class StrategyConfig(BaseModel):
    name: str
    enabled: bool
    parameters: Dict[str, Any]

# Authentication
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = User(**payload)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Implement your authentication logic here
    if form_data.username == "admin" and form_data.password == "password":
        token = jwt.encode(
            {"username": form_data.username, "exp": datetime.utcnow() + timedelta(days=1)},
            settings.SECRET_KEY
        )
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

# Trading endpoints
@router.post("/trade")
async def execute_trade(
    trade_request: TradeRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute a manual trade with error handling."""
    try:
        trading_service = TradingService(strategy_manager, model)
        result = await trading_service.execute_trade({
            "symbol": trade_request.symbol,
            "amount": trade_request.amount,
            "action": trade_request.action,
            "strategy": trade_request.strategy
        })
        return result
    except TradingError as e:
        raise ErrorHandler.handle_api_error(e)
    except Exception as e:
        logger.error(f"Unexpected error in trade endpoint: {str(e)}")
        raise ErrorHandler.handle_api_error(e)

@router.get("/predictions")
async def get_predictions(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get model predictions for a symbol."""
    try:
        # Implement prediction logic
        return {
            "symbol": symbol,
            "predictions": {
                "price": 100.0,
                "direction": "up",
                "confidence": 0.85
            }
        }
    except Exception as e:
        logger.error(f"Error getting predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance(
    timeframe: str = "1d",
    current_user: User = Depends(get_current_user)
):
    """Get trading performance metrics."""
    try:
        # Implement performance metrics calculation
        return {
            "total_return": 0.15,
            "sharpe_ratio": 1.2,
            "max_drawdown": -0.05,
            "win_rate": 0.65
        }
    except Exception as e:
        logger.error(f"Error getting performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_strategies(current_user: User = Depends(get_current_user)):
    """Get available trading strategies."""
    try:
        return {
            "strategies": [
                {"name": "MACD", "enabled": True},
                {"name": "RSI", "enabled": True}
            ]
        }
    except Exception as e:
        logger.error(f"Error getting strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies/configure")
async def configure_strategy(
    config: StrategyConfig,
    current_user: User = Depends(get_current_user)
):
    """Configure a trading strategy."""
    try:
        # Implement strategy configuration logic
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error configuring strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check critical services
        db_healthy = await check_database_connection()
        model_healthy = await check_model_status()
        ws_healthy = await check_websocket_status()
        
        if all([db_healthy, model_healthy, ws_healthy]):
            return {"status": "healthy"}
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "details": {
                        "database": db_healthy,
                        "model": model_healthy,
                        "websocket": ws_healthy
                    }
                }
            )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        ) 

# Add at module level
strategy_manager = StrategyManager()
model = TradingModel() 