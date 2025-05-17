# File: app/core/config.py
# Description: Application configuration settings

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Force reload of environment variables from the .env file
dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path, override=True)
else:
    print(f"WARNING: .env file not found at {dotenv_path}")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Oil API"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Add your Next.js frontend URL

    # Database settings
    DATABASE_URI: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    SQL_ECHO: bool = False

    # Cloudflare R2 settings
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    R2_REGION: str = "auto"
    R2_ENDPOINT_URL: str = "https://r2.cloudflarestorage.com"
    R2_PUBLIC_URL: str  # Public URL for the bucket (required)
    R2_PRESIGNED_URL_EXPIRATION: int = 20  # Expiration time for pre-signed URLs in seconds (very short for security)

    # Logging configuration
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO").upper()  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # OAuth JWT settings
    JWKS_URI: str = os.environ.get("JWKS_URI", "http://localhost:8080/realms/master/protocol/openid-connect/certs")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()