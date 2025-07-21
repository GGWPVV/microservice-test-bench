import os
import redis.asyncio as redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def get_redis():
    return redis_client

async def get_discount_from_cache(redis, username):
    value = await redis.get(f"discount:{username}")
    return float(value) if value else None

async def set_discount_cache(redis, username, discount, ttl=3600):
    await redis.set(f"discount:{username}", discount, ex=ttl)
