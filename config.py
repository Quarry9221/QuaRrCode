from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List

class Settings(BaseSettings):
    bot_token: str = Field(..., description="Telegram Bot API token")
    api_url: str = Field(default="http://localhost:8000", description="Base URL for FastAPI backend")
    api_key: str = Field(..., description="API key for FastAPI authentication")
    database_url: str = Field(
        default="postgresql+asyncpg://qr_bot:1234@localhost:5432/qr_bot_db",
        description="Async database URL (PostgreSQL recommended)"
    )
    redis_url: Optional[str] = Field(default=None, description="Redis URL for caching or rate limiting")
    max_qr_text_length: int = Field(
        default=2048,
        ge=1,
        le=4096,
        description="Maximum length of text for QR code"
    )
    allowed_file_types: List[str] = Field(
        default=["image/png", "image/jpeg", "text/plain"],
        description="Allowed MIME types for uploaded files"
    )
    max_file_size_mb: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum file size in MB for uploads"
    )
    log_level: str = Field(
        default="DEBUG",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    default_qr_settings: dict = Field(
        default={
            "fmt": "PNG",
            "size": 10,
            "fg": "black",
            "bg": "white"
        },
        description="Default settings for QR code generation"
    )
    allowed_qr_formats: List[str] = Field(
        default=["PNG", "SVG"],
        description="Supported QR code formats"
    )
    allowed_qr_sizes: List[int] = Field(
        default=[5, 10, 15, 20, 25],
        description="Supported QR code sizes"
    )
    allowed_colors: List[str] = Field(
        default=["black", "blue", "red", "green", "white", "yellow"],
        description="Supported colors for QR code foreground and background"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()