ROLL_KEY_PREFIX = "roll_done:"

async def mark_roll(redis, user_id: str):
    await redis.set(f"{ROLL_KEY_PREFIX}{user_id}", "1", ex=86400)  # 24ч

async def has_rolled(redis, user_id: str) -> bool:
    return await redis.exists(f"{ROLL_KEY_PREFIX}{user_id}") == 1
