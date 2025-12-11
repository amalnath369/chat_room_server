from fastapi import WebSocket, WebSocketDisconnect
import logging
from .connection_manager import ConnectionManager


logger = logging.getLogger(__name__)


class WebSocketHandler:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection lifecycle"""
        await self.connection_manager.connect(websocket)
        
        try:
            await self.connection_manager.receive_and_process(websocket)
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected normally")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await websocket.close(code=1011)