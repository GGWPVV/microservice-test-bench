from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database
import random

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
    score_entry = db.query(models.UserScore).filter_by(user_id=user_id).first()

    if score_entry:
        raise HTTPException(status_code=400, detail="Ты уже использовал свой шанс!")

    score_value = random.randint(1, 1000)
    new_score = models.UserScore(user_id=user_id, score=score_value)
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    return {"user_id": user_id, "score": score_value}
