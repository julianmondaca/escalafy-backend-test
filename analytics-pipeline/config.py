"""
Configuration module for the analytics pipeline.
Reads environment variables and validates them using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings derived from environment variables.
    """
    database_url: str
    redis_url: str
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    reporting_port: int = 8001
    worker_batch_size: int = 50
    worker_poll_interval_seconds: float = 1.0

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()
