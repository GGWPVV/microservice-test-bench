from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import random
from datetime import datetime
from database import get_db
from models import UserScore
from redis_client import get_redis, mark_rolled, has_rolled
import models, database, json
from user_client import get_user
from kafka_producer import publish_event
import logging

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)
from kafka_producer import publish_event, start_kafka_producer, stop_kafka_producer
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
@app.on_event("startup")
async def on_startup():
    logging.info("App is starting up...")
    await start_kafka_producer()

@app.on_event("shutdown")
async def on_shutdown():
    logging.info("App is shutting down...")
    await stop_kafka_producer()

@app.post("/roll")
async def draw_score(
    Authorization: str = Header(...), 
    db: Session = Depends(get_db)
):
    redis = await get_redis()
    await redis.delete("leaderboard_top10")

    user_data = get_user(Authorization)
    if not user_data:
        raise HTTPException(status_code=403, detail="Invalid token")

    user_id = user_data["id"]
    username = user_data["username"]

    # 2. Check if user has already rolled
    if await has_rolled(redis, user_id):
        raise HTTPException(status_code=400, detail="You have already rolled.")

    # 3. Generate and save score
    score_value = random.randint(1, 1_000_000)
    existing = db.query(models.UserScore).filter_by(user_id=user_id).first()
    if existing:
        existing.score = score_value
        existing.created_at = datetime.utcnow()
        new_score = existing
    else: 
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
        logging.info("Leaderboard: Cache hit")
        return json.loads(cached)

    print("Cache miss — querying DB")
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
    return result

@app.delete("/leaderboard/cache")
async def clear_leaderboard_cache(redis = Depends(get_redis)):
    await redis.delete("leaderboard_top10")
    logging.info("Leaderboard cache cleared by user request")
    return {"detail": "Leaderboard cache cleared"}
