"""
Configuration management for the Autonomous Financial Research Agent
"""
import os
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    """Application settings with validation"""

    # API Keys
    openai_api_key: str
    serpapi_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None

    # Application settings
    app_name: str = "Autonomous Financial Research Agent"
    version: str = "1.0.0"
    debug: bool = False

    # Agent settings
    max_iterations: int = 10
    temperature: float = 0.7
    max_tokens: int = 500

    # Cache settings
    cache_ttl_hours: int = 24
    cache_dir: str = "./cache"

    # Vector DB settings
    vector_db_dir: str = "./vector_db/data"

    # Logging settings
    log_level: str = "INFO"
    log_dir: str = "./logs"

    # API settings
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = ["http://localhost:8501", "http://127.0.0.1:8501"]

    # Rate limiting
    requests_per_minute: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator('openai_api_key')
    def validate_openai_key(cls, v):
        if not v or v == "your_openai_api_key_here":
            raise ValueError("Valid OpenAI API key is required")
        return v

    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v

    @validator('max_iterations')
    def validate_max_iterations(cls, v):
        if v < 1 or v > 20:
            raise ValueError("Max iterations must be between 1 and 20")
        return v

# Global settings instance - created lazily
_settings_instance = None

def get_settings() -> Settings:
    """Get settings instance, creating it if necessary"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance

# For backward compatibility, try to create settings but don't fail on import
try:
    settings = get_settings()
except Exception:
    # Settings will be created when actually needed
    settings = None