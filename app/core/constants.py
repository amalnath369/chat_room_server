from enum import Enum


class Commands(str, Enum):
    LIST = "/list"


class WebSocketCloseCodes(int, Enum):
    NORMAL_CLOSURE = 1000
    GOING_AWAY = 1001
    INVALID_PAYLOAD = 1007
    POLICY_VIOLATION = 1008
    INTERNAL_ERROR = 1011


class ErrorMessages(str, Enum):
    INVALID_JSON = "Invalid JSON payload"
    USERNAME_REQUIRED = "Username is required"
    TOPIC_REQUIRED = "Topic is required"
    INVALID_PAYLOAD_FORMAT = "Payload must contain 'username' and 'topic'"