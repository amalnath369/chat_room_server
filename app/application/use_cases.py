from typing import Dict, List, Optional
import time
import asyncio
from ..domain.entities import Message, User
from ..domain.repository import ChatRepository
from ..core.constants import Commands


class ChatUseCases:
    def __init__(self, repository: ChatRepository):
        self.repository = repository
    
    async def handle_user_join(self, topic_name: str, desired_username: str, websocket) -> tuple[str, User]:
        """Handle user joining a topic with unique username generation"""
        unique_username = await self.repository.get_unique_username(topic_name, desired_username)
        
        topic = await self.repository.get_topic(topic_name)
        if not topic:
            topic = await self.repository.create_topic(topic_name)
        
        user = User(username=unique_username, websocket=websocket)
        await self.repository.add_user_to_topic(topic_name, user)
        
        return unique_username, user
    
    async def handle_message(self, topic_name: str, username: str, content: str) -> Optional[Message]:
        """Handle sending a message to a topic"""
        if content.strip() == Commands.LIST:
            return None
        
        message = Message(
            username=username,
            content=content,
            timestamp=time.time(),
            topic=topic_name
        )
        
        await self.repository.add_message(topic_name, message)
        return message
    
    async def handle_list_command(self, topic_name: str) -> Dict:
        """Handle /list command"""
        topics = await self.repository.get_all_topics()
        
        active_topics = []
        for name, topic in topics.items():
            active_topics.append(f"{name} ({topic.user_count} users)")
        
        return {
            "type": "topic_list",
            "topics": active_topics
        }
    
    async def handle_user_leave(self, topic_name: str, username: str) -> None:
        """Handle user leaving a topic"""
        await self.repository.remove_user_from_topic(topic_name, username)
        
        topic = await self.repository.get_topic(topic_name)
        if topic and topic.user_count == 0:
            await self.repository.delete_topic(topic_name)
    
    async def cleanup_expired_messages(self, ttl: int):
        """Cleanup expired messages from all topics"""
        while True:
            try:
                current_time = time.time()
                topics = await self.repository.get_all_topics()
                
                for topic in topics.values():
                    topic.remove_expired_messages(current_time, ttl)
                
                await asyncio.sleep(5)  # Run cleanup every 5 seconds
            except Exception as e:
                print(f"Error in cleanup task: {e}")
                await asyncio.sleep(5)