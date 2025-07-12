import json
import os
from typing import Any, Optional, Union, Dict
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

class RedisService:
    """Service for Redis caching"""
    
    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL) if REDIS_URL else None
        
    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Set value in Redis cache with expiration"""
        if not self.redis_client:
            return False
            
        try:
            # Serialize value to JSON string
            serialized_value = json.dumps(value)
            self.redis_client.set(key, serialized_value, ex=expire_seconds)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.redis_client:
            return None
            
        try:
            value = self.redis_client.get(key)
            if value:
                # Deserialize JSON string to Python object
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        if not self.redis_client:
            return False
            
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> bool:
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return False
            
        try:
            cursor = 0
            while True:
                cursor, keys = self.redis_client.scan(cursor, match=pattern, count=100)
                if keys:
                    self.redis_client.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception as e:
            print(f"Redis clear_pattern error: {e}")
            return False

# Singleton instance
redis_service = RedisService()
