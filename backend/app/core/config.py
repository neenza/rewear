import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseModel):
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    # 60 minutes * 24 hours * 7 days = 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))
    
    # CORS Configuration - Allow all origins for demo
    CORS_ORIGINS: List[str] = ["*"]
    
    # AWS S3 Configuration for file storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    # AWS S3 Configuration for file storage
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: str = os.getenv("AWS_STORAGE_BUCKET_NAME", "rewear-uploads")


settings = Settings()
