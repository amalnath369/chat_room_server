import json
import time
from typing import Dict, Any
import asyncio
from ..domain.entities import Message
from ..core.constants import ErrorMessages, Commands
from .use_cases import ChatUseCases


class ChatService:
    def __init__(self, use_cases: ChatUseCases, message_ttl: int = 30):
        self.use_cases = use_cases
        self.message_ttl = message_ttl
    
    async def process_connection(self, websocket, data: Dict[str, Any]) -> tuple[str, str]:
        """Process initial connection"""
        if not data.get("username"):
            await websocket.send_json({"error": ErrorMessages.USERNAME_REQUIRED})
            raise ValueError(ErrorMessages.USERNAME_REQUIRED)
        
        if not data.get("topic"):
            await websocket.send_json({"error": ErrorMessages.TOPIC_REQUIRED})
            raise ValueError(ErrorMessages.TOPIC_REQUIRED)
        
        username = data["username"]
        topic = data["topic"]
        
        unique_username, user = await self.use_cases.handle_user_join(
            topic, username, websocket
        )
        
        return unique_username, topic
    
    async def process_message(self, topic: str, username: str, content: str, websocket) -> None:
        """Process incoming message"""
        if content.strip() == Commands.LIST:
            # Handle list command
            response = await self.use_cases.handle_list_command(topic)
            await websocket.send_json(response)
            return
        
        # Handle regular message
        message = await self.use_cases.handle_message(topic, username, content)
        
        if message:
            # Send acknowledgment to sender
            await websocket.send_json({
                "type": "acknowledgment",
                "message_id": message.id,
                "timestamp": message.timestamp
            })
            
            # Broadcast to other users in topic
            await self._broadcast_message(message)
            
            # Schedule message cleanup
            asyncio.create_task(self._schedule_message_cleanup(topic, message.id))
    
    async def _broadcast_message(self, message: Message):
        """Broadcast message to all users in topic except sender"""
        topic = await self.use_cases.repository.get_topic(message.topic)
        if not topic:
            return
        
        message_dict = message.to_dict()
        
        for user in topic.users.values():
            if user.username != message.username:
                try:
                    await user.websocket.send_json(message_dict)
                except Exception as e:
                    print(f"Error broadcasting to {user.username}: {e}")
    
    async def _schedule_message_cleanup(self, topic_name: str, message_id: str):
        """Schedule message cleanup after TTL"""
        await asyncio.sleep(self.message_ttl)
        
        # In a real implementation, you'd remove the message by ID
        # For now, the periodic cleanup will handle it
    
    async def handle_disconnection(self, topic: str, username: str):
        """Handle user disconnection"""
        await self.use_cases.handle_user_leave(topic, username)