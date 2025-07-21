from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import random
from datetime import datetime
from database import get_db
from models import UserScore
from redis_client import get_redis
import models, database, json
from user_client import get_user

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)



@app.post("/roll")
async def draw_score(
    Authorization: str = Header(...), 
    db: Session = Depends(get_db)
):
    # Take Redis client
    redis = await get_redis()

    # Invalidate leaderboard cache
    await redis.delete("leaderboard_top10")

    # 1. Check user token
    user_data = get_user(Authorization)
    if not user_data:
        raise HTTPException(status_code=403, detail="Invalid token")

    user_id = user_data["id"]
    username = user_data["username"]

    # 2. Check if user has already rolled
    if await redis.get(f"already_rolled:{user_id}"):
        raise HTTPException(status_code=400, detail="You have already rolled.")

    # 3. Generate and save score
    score_value = random.randint(1, 1_000_000)
    existing = db.query(models.UserScore).filter_by(user_id=user_id).first()
    if existing:
        existing.score = score_value
        existing.created_at = datetime.utcnow()
    else: 
        new_score = models.UserScore(
            user_id=user_id,
            username=username,
            score=score_value,
            created_at=datetime.utcnow()
    )
        db.add(new_score)
    db.commit()
    
    

    # 4. Flag user as having rolled
    await redis.set(f"already_rolled:{user_id}", "1", ex=60*60*24*365)

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
        print("Cache hit")
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
    return {"detail": "Leaderboard cache cleared"}
