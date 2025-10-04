import sys
from loguru import logger
import os

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
# Ensure log directory exists
_log_dir = "logs"
try:
    os.makedirs(_log_dir, exist_ok=True)
except Exception:
    # Fallback to stdout only if directory creation fails
    pass

logger.add(
    os.path.join(_log_dir, "trading_agent.log"),
    rotation="500 MB",
    retention="10 days",
    level="DEBUG"
)

def get_logger():
    return logger 