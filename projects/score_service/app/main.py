from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database, random
from user_client import get_user  # Импорт функции для запроса к User Service

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/draw-score")
def draw_score(user_id: str, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь в User Service
    user_data = get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    score_entry = db.query(models.UserScore).filter_by(user_id=user_id).first()

    if score_entry:
        raise HTTPException(status_code=400, detail="Ты уже использовал свой шанс!")

    score_value = random.randint(1, 1000)
    new_score = models.UserScore(user_id=user_id, score=score_value)
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    return {"user_id": user_id, "score": score_value}
