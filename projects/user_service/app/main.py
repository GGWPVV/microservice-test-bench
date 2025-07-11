from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import User, UserCreate, UserOut

from fastapi.middleware.cors import CORSMiddleware

# создаём таблицы, если их нет
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS (если надо)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# зависимость получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST /users — создать пользователя
@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        username=user.username,
        age=user.age,
        city=user.city,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# GET /userslist — получить список пользователей
@app.get("/userslist", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
