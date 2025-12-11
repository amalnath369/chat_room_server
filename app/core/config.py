from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "WebSocket Chat Server"
    host: str = "0.0.0.0"
    port: int = 8000
    message_ttl: int = 30  # seconds
    debug: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()