# redis_client.py

import os
import json
import redis.asyncio as redis
from logger_config import setup_logger

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
logger = setup_logger("redis_client")

LEADERBOARD_CACHE_KEY = "top_10_users"
ROLL_KEY_PREFIX = "already_rolled:"  # используем единый префикс


async def get_redis():
    return redis_client

# Leaderboard cache
async def cache_leaderboard(data: list):
    await redis_client.set(LEADERBOARD_CACHE_KEY, json.dumps(data), ex=60)
    logger.info({"event": "cache_leaderboard", "count": len(data)})

async def get_cached_leaderboard():
    raw = await redis_client.get(LEADERBOARD_CACHE_KEY)
    if raw:
        logger.info({"event": "get_cached_leaderboard", "status": "hit"})
        return json.loads(raw)
    logger.info({"event": "get_cached_leaderboard", "status": "miss"})
    return None

# Roll flag
async def mark_rolled(redis, user_id: str):
    await redis.set(f"{ROLL_KEY_PREFIX}{user_id}", "1", ex=60*60*24*365)  # 1 год
    logger.info({"event": "mark_rolled", "user_id": user_id})

async def has_rolled(redis, user_id: str) -> bool:
    result = await redis.exists(f"{ROLL_KEY_PREFIX}{user_id}") == 1
    logger.info({"event": "has_rolled", "user_id": user_id, "result": result})
    return result
