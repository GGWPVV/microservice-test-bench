from fastapi import FastAPI, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
import random
from datetime import datetime
from database import get_db
from models import UserScore
from redis_client import get_redis, mark_rolled, has_rolled
import models, database, json
from user_client import get_user
from kafka_producer import publish_event
from logger_config import setup_logger

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)
from kafka_producer import publish_event, start_kafka_producer, stop_kafka_producer
logger = setup_logger("score_service")

@app.on_event("startup")
async def on_startup():
    logger.info({"event": "startup", "message": "App is starting up..."})
    await start_kafka_producer()

@app.on_event("shutdown")
async def on_shutdown():
    logger.info({"event": "shutdown", "message": "App is shutting down..."})
    await stop_kafka_producer()

@app.post("/roll")
async def draw_score(
    Authorization: str = Header(...), 
    db: Session = Depends(get_db)
):
    logger.info({"event": "roll_request", "message": "Roll endpoint called", "Authorization": Authorization})
    redis = await get_redis()
    await redis.delete("leaderboard_top10")

    user_data = get_user(Authorization)
    if not user_data:
        logger.warning({"event": "invalid_token", "message": "Invalid token", "Authorization": Authorization})
        raise HTTPException(status_code=403, detail="Invalid token")

    user_id = user_data["id"]
    username = user_data["username"]

    # 2. Check if user has already rolled
    if await has_rolled(redis, user_id):
        logger.info({"event": "already_rolled", "user_id": user_id, "username": username})
        raise HTTPException(status_code=400, detail="You have already rolled.")

    # 3. Generate and save score
    score_value = random.randint(1, 1_000_000)
    existing = db.query(models.UserScore).filter_by(user_id=user_id).first()
    if existing:
        logger.info({"event": "score_update", "user_id": user_id, "old_score": existing.score, "new_score": score_value})
        existing.score = score_value
        existing.created_at = datetime.utcnow()
        new_score = existing
    else: 
        logger.info({"event": "score_create", "user_id": user_id, "score": score_value})
        new_score = models.UserScore(
            user_id=user_id,
            username=username,
            score=score_value,
            created_at=datetime.utcnow()
        )
        db.add(new_score)
    db.commit()

    await publish_event("score.rolled", {
        "user_id": user_id,
        "username": username,
        "score": score_value
    })

    # 4. Flag user as having rolled
    await mark_rolled(redis, user_id)

    logger.info({"event": "roll_success", "user_id": user_id, "username": username, "score": score_value})
    return {
        "username": username,
        "score": score_value,
        "timestamp": new_score.created_at
    }

@app.get("/leaderboard")
async def get_leaderboard(
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
):
    cached = await redis.get("leaderboard_top10")
    if cached:
        logger.info({"event": "leaderboard_cache_hit"})
        return json.loads(cached)

    logger.info({"event": "leaderboard_cache_miss"})
    top_players = (
        db.query(UserScore)
        .order_by(UserScore.score.desc())
        .limit(10)
        .all()
    )

    result = [
        {
            "username": entry.username,
            "score": entry.score,
            "play_date": entry.created_at.isoformat()
        }
        for entry in top_players
    ]

    await redis.set("leaderboard_top10", json.dumps(result), ex=60)  # TTL 60s
    logger.info({"event": "leaderboard_cache_set", "count": len(result)})
    return result

@app.delete("/leaderboard/cache")
async def clear_leaderboard_cache(redis = Depends(get_redis)):
    await redis.delete("leaderboard_top10")
    logger.info({"event": "leaderboard_cache_cleared"})
    return {"detail": "Leaderboard cache cleared"}

logger = setup_logger("http_logger")

@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    logger.info({
        "event": "http_request",
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
    })
    response = await call_next(request)
    logger.info({
        "event": "http_response",
        "status_code": response.status_code,
        "url": str(request.url),
    })
    return response
