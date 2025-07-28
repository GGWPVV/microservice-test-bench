import os
import redis.asyncio as redis
from logger_config import setup_logger

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
logger = setup_logger("redis_client")

async def get_redis():
    return redis_client

class RedisCache:
    """Базовый класс для работы с Redis кэшем"""
    
    @staticmethod
    async def get(key: str):
        value = await redis_client.get(key)
        logger.info({"event": "cache_get", "key": key, "hit": value is not None})
        return value
    
    @staticmethod
    async def set(key: str, value, ttl: int = 3600):
        await redis_client.set(key, value, ex=ttl)
        logger.info({"event": "cache_set", "key": key, "ttl": ttl})
    
    @staticmethod
    async def delete(key: str):
        result = await redis_client.delete(key)
        logger.info({"event": "cache_delete", "key": key, "deleted": result})
        return result
    
    @staticmethod
    async def exists(key: str) -> bool:
        result = await redis_client.exists(key) == 1
        logger.info({"event": "cache_exists", "key": key, "exists": result})
        return result