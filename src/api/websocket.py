from fastapi import WebSocket
from typing import List, Dict, Any
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.pair_subscriptions: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, pairs: List[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if pairs:
            for pair in pairs:
                if pair not in self.pair_subscriptions:
                    self.pair_subscriptions[pair] = []
                self.pair_subscriptions[pair].append(websocket)
                
    async def broadcast_trade(self, pair: str, trade_data: Dict[str, Any]):
        """Broadcast trade updates to subscribed clients"""
        if pair in self.pair_subscriptions:
            for connection in self.pair_subscriptions[pair]:
                try:
                    await connection.send_json(trade_data)
                except Exception as e:
                    await self.disconnect(connection) 