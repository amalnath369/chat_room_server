from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class User:
    username: str
    websocket: any
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    joined_at: datetime = field(default_factory=datetime.now)


@dataclass
class Message:
    username: str
    content: str
    timestamp: float
    topic: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self):
        return {
            "username": self.username,
            "message": self.content,
            "timestamp": self.timestamp,
            "topic": self.topic
        }


@dataclass
class Topic:
    name: str
    users: dict[str, User] = field(default_factory=dict)
    messages: list[Message] = field(default_factory=list)
    
    @property
    def user_count(self):
        return len(self.users)
    
    def add_user(self, user: User):
        self.users[user.username] = user
    
    def remove_user(self, username: str):
        if username in self.users:
            del self.users[username]
    
    def add_message(self, message: Message):
        self.messages.append(message)
    
    def remove_expired_messages(self, current_time: float, ttl: int):
        self.messages = [
            msg for msg in self.messages 
            if current_time - msg.timestamp < ttl
        ]