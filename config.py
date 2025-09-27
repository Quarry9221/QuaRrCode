from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    bot_token: str
    database_url: Optional[str] = "sqlite:///bot.db"
    redis_url: Optional[str] = None
    max_qr_text_length: int = 2048
    allowed_file_types: list[str] = ["image/png", "image/jpeg", "text/plain"]
    max_file_size_mb: int = 10

    class Config:
        env_file = ".env"

settings = Settings()