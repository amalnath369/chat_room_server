import asyncio
from typing import Dict, Optional
from ..domain.repository import ChatRepository
from ..domain.entities import Topic, User


class InMemoryChatRepository(ChatRepository):
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self._lock = asyncio.Lock()
    
    async def get_topic(self, topic_name: str) -> Optional[Topic]:
        async with self._lock:
            return self.topics.get(topic_name)
    
    async def create_topic(self, topic_name: str) -> Topic:
        async with self._lock:
            if topic_name not in self.topics:
                self.topics[topic_name] = Topic(name=topic_name)
            return self.topics[topic_name]
    
    async def delete_topic(self, topic_name: str) -> None:
        async with self._lock:
            if topic_name in self.topics:
                del self.topics[topic_name]
    
    async def get_all_topics(self) -> Dict[str, Topic]:
        async with self._lock:
            return self.topics.copy()
    
    async def add_user_to_topic(self, topic_name: str, user: User) -> None:
        async with self._lock:
            if topic_name in self.topics:
                self.topics[topic_name].add_user(user)
    
    async def remove_user_from_topic(self, topic_name: str, username: str) -> None:
        async with self._lock:
            if topic_name in self.topics:
                self.topics[topic_name].remove_user(username)
    
    async def add_message(self, topic_name: str, message) -> None:
        async with self._lock:
            if topic_name in self.topics:
                self.topics[topic_name].add_message(message)
    
    async def get_unique_username(self, topic_name: str, desired_username: str) -> str:
        async with self._lock:
            if topic_name not in self.topics:
                return desired_username
            
            topic = self.topics[topic_name]
            if desired_username not in topic.users:
                return desired_username
            
            # Find unique username with numeric suffix
            counter = 2
            while f"{desired_username}#{counter}" in topic.users:
                counter += 1
            
            return f"{desired_username}#{counter}"