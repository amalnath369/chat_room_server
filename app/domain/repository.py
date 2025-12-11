from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from ..domain.entities import Topic, User, Message


class ChatRepository(ABC):
    @abstractmethod
    async def get_topic(self, topic_name: str) -> Optional[Topic]:
        pass
    
    @abstractmethod
    async def create_topic(self, topic_name: str) -> Topic:
        pass
    
    @abstractmethod
    async def delete_topic(self, topic_name: str) -> None:
        pass
    
    @abstractmethod
    async def get_all_topics(self) -> Dict[str, Topic]:
        pass
    
    @abstractmethod
    async def add_user_to_topic(self, topic_name: str, user: User) -> None:
        pass
    
    @abstractmethod
    async def remove_user_from_topic(self, topic_name: str, username: str) -> None:
        pass
    
    @abstractmethod
    async def add_message(self, topic_name: str, message: Message) -> None:
        pass
    
    @abstractmethod
    async def get_unique_username(self, topic_name: str, desired_username: str) -> str:
        pass