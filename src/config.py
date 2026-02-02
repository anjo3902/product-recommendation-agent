# src/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Google API
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/product_recommendation"
    )
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-key")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "True") == "True"
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()

# Validate critical settings
if not settings.google_api_key or settings.google_api_key == "your_google_api_key_here":
    print("⚠️  WARNING: GOOGLE_API_KEY not set! Please update your .env file")
    print("   Get your API key from: https://makersuite.google.com/app/apikey")
