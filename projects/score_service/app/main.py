from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import random
from datetime import datetime
from database import get_db
from models import UserScore

import models, database
from user_client import get_user

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)



@app.post("/roll")
def draw_score(
    Authorization: str = Header(...), 
    db: Session = Depends(get_db)
):
    # 1. Check user token
    user_data = get_user(Authorization)
    if not user_data:
        raise HTTPException(status_code=403, detail="Invalid token or user not found")
    
    user_id = user_data["id"]
    username = user_data["username"]

    # 2. Check if user has already played
    existing_score = db.query(models.UserScore).filter_by(user_id=user_id).first()
    if existing_score:
        raise HTTPException(status_code=400, detail= "You have already played")

    # 3. Generate a random score and save it
    score_value = random.randint(1, 1_000_000)
    new_score = models.UserScore(
        user_id=user_id,
        username=username,
        score=score_value,
        created_at=datetime.utcnow()
    )
    db.add(new_score)
    db.commit()

    return {
        "username": username,
        "score": score_value,
        "timestamp": new_score.created_at
    }

@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    top_players = (
        db.query(UserScore)
        .order_by(UserScore.score.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "username": entry.username,
            "score": entry.score,
            "play_date": entry.created_at
        }
        for entry in top_players
    ]
