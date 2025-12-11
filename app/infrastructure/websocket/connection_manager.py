import json
import logging
from typing import Dict, Any
from fastapi import WebSocket
from ...core.constants import ErrorMessages


logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self, chat_service):
        self.chat_service = chat_service
        self.active_connections: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept WebSocket connection"""
        await websocket.accept()
        logger.info("New WebSocket connection established")
    
    async def receive_and_process(self, websocket: WebSocket):
        """Main loop to receive and process messages"""
        connection_info = None
        
        try:
            data = await websocket.receive_text()
            connection_info = await self._handle_initial_data(websocket, data)
            
            if not connection_info:
                return
            
            username, topic = connection_info
            
            self.active_connections[username] = {
                "websocket": websocket,
                "topic": topic
            }
            
            logger.info(f"User {username} joined topic {topic}")
            
            while True:
                data = await websocket.receive_text()
                await self.chat_service.process_message(topic, username, data, websocket)
                
        except json.JSONDecodeError:
            await websocket.send_json({"error": ErrorMessages.INVALID_JSON})
            logger.warning("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error in connection: {e}")
        finally:
            if connection_info:
                username, topic = connection_info
                await self._handle_disconnect(username, topic)
    
    async def _handle_initial_data(self, websocket: WebSocket, data: str) -> tuple:
        """Handle initial connection data"""
        try:
            json_data = json.loads(data)
            
            if not isinstance(json_data, dict) or 'username' not in json_data or 'topic' not in json_data:
                await websocket.send_json({"error": ErrorMessages.INVALID_PAYLOAD_FORMAT})
                return None
            
            username, topic = await self.chat_service.process_connection(
                websocket, json_data
            )
            
            return username, topic
            
        except (json.JSONDecodeError, ValueError) as e:
            await websocket.send_json({"error": str(e)})
            return None
    
    async def _handle_disconnect(self, username: str, topic: str):
        """Handle user disconnection"""
        if username in self.active_connections:
            del self.active_connections[username]
        
        await self.chat_service.handle_disconnection(topic, username)
        logger.info(f"User {username} disconnected from topic {topic}")