"""
Redis connection management
"""
import redis.asyncio as redis
from app.core.config import settings


class RedisManager:
    """Redis connection manager"""
    
    client: redis.Redis = None
    
    @classmethod
    async def connect(cls):
        """Connect to Redis"""
        cls.client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls.client:
            await cls.client.close()
    
    @classmethod
    async def get(cls, key: str):
        """Get value from Redis"""
        return await cls.client.get(key)
    
    @classmethod
    async def set(cls, key: str, value: str, expire: int = None):
        """Set value in Redis"""
        return await cls.client.set(key, value, ex=expire)
    
    @classmethod
    async def delete(cls, key: str):
        """Delete key from Redis"""
        return await cls.client.delete(key)


# Initialize Redis manager
redis_manager = RedisManager()
