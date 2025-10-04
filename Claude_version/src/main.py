import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.api.routes import router
from src.config.settings import settings
from src.utils.logger import get_logger
from src.api.websocket import WebSocketManager
from src.services.event_service import EventService
import asyncio
import json

logger = get_logger()

app = FastAPI(title="AI Trading Agent")
app.include_router(router, prefix="/api/v1")

websocket_manager = WebSocketManager()
event_service = EventService()

@app.websocket("/ws/trades")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                parsed_data = json.loads(data)
                # Handle parsed_data
            except json.JSONDecodeError as e:
                logger.error(f"Invalid message format: {str(e)}")
                await websocket.send_text(json.dumps({
                    "error": "Invalid message format"
                }))
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    # Start the event service
    asyncio.create_task(event_service.start())

@app.on_event("shutdown")
async def shutdown_event():
    # Stop the event service
    await event_service.stop()

if __name__ == "__main__":
    try:
        logger.info("Starting AI Trading Agent")
        uvicorn.run(
            "main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True
        )
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        raise 