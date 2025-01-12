from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any
from src.utils.logger import get_logger

logger = get_logger()

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            'trades': set(),
            'predictions': set(),
            'performance': set()
        }
    
    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        self.active_connections[channel].add(websocket)
        logger.info(f"Client connected to {channel} channel")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        self.active_connections[channel].remove(websocket)
        logger.info(f"Client disconnected from {channel} channel")
    
    async def broadcast(self, message: Dict[str, Any], channel: str):
        """Broadcast message to all connected clients in a channel."""
        disconnected = set()
        
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, channel) 