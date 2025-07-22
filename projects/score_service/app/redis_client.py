# redis_client.py

import os
import json
import redis.asyncio as redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

LEADERBOARD_CACHE_KEY = "top_10_users"
ROLL_KEY_PREFIX = "already_rolled:"  # используем единый префикс


async def get_redis():
    return redis_client

# Leaderboard cache
async def cache_leaderboard(data: list):
    await redis_client.set(LEADERBOARD_CACHE_KEY, json.dumps(data), ex=60)

async def get_cached_leaderboard():
    raw = await redis_client.get(LEADERBOARD_CACHE_KEY)
    return json.loads(raw) if raw else None

# Roll flag
async def mark_rolled(redis, user_id: str):
    await redis.set(f"{ROLL_KEY_PREFIX}{user_id}", "1", ex=60*60*24*365)  # 1 год

async def has_rolled(redis, user_id: str) -> bool:
    return await redis.exists(f"{ROLL_KEY_PREFIX}{user_id}") == 1
