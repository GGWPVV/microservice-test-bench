import os
import redis.asyncio as redis
from logger_config import setup_logger

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
logger = setup_logger("redis_client")

async def get_redis():
    logger.info({"event": "get_redis", "message": "Getting Redis client"})
    return redis_client

async def get_discount_from_cache(redis, username):
    value = await redis.get(f"discount:{username}")
    if value:
        logger.info({"event": "discount_cache_hit", "username": username, "discount": value})
    else:
        logger.info({"event": "discount_cache_miss", "username": username})
    return float(value) if value else None

async def set_discount_cache(redis, username, discount, ttl=3600):
    await redis.set(f"discount:{username}", discount, ex=ttl)
    logger.info({"event": "discount_cache_set", "username": username, "discount": discount, "ttl": ttl})
