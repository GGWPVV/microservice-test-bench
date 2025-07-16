from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from uuid import UUID
import random
import models, database
from user_client import get_user
from datetime import datetime

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/roll")
def draw_score(Authorization: str = Header(...), db: Session = Depends(get_db)):
    # Авторизация и извлечение user_id из JWT
    user_data = get_user(Authorization)
    if not user_data:
        raise HTTPException(status_code=403, detail="Invalid token or user not found")
    
    user_id = user_data["id"]
    username = user_data["username"]

    # Проверка, крутил ли уже рулетку
    existing_score = db.query(models.UserScore).filter_by(user_id=user_id).first()
    if existing_score:
        raise HTTPException(status_code=400, detail="Ты уже использовал рулетку")

    # Генерация числа и запись
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
