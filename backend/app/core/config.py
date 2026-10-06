import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Railway Rakshak Cyber-NOC"
    VERSION: str = "4.2.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "railway-rakshak-super-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database: Defaults to local SQLite, easily overridden with postgresql:// in Docker / Production
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./railway_rakshak.db"
    )
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Telemetry & Simulator
    SIMULATOR_ENABLED: bool = os.getenv("SIMULATOR_ENABLED", "true").lower() == "true"
    SIMULATOR_INTERVAL_SECONDS: float = float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "3.0"))
    
    class Config:
        case_sensitive = True

settings = Settings()
