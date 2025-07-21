import redis
import os
import json

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

LEADERBOARD_CACHE_KEY = "top_10_users"
ROLL_CACHE_PREFIX = "roll_done:"  # по user_id

def cache_leaderboard(data: list):
    r.set(LEADERBOARD_CACHE_KEY, json.dumps(data), ex=60)   # TTL 60 seconds

def get_cached_leaderboard():
    raw = r.get(LEADERBOARD_CACHE_KEY)
    return json.loads(raw) if raw else None

def mark_user_rolled(user_id: str):
    r.set(f"{ROLL_CACHE_PREFIX}{user_id}", "1")

def has_user_rolled(user_id: str) -> bool:
    return r.exists(f"{ROLL_CACHE_PREFIX}{user_id}") == 1
