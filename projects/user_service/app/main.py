from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import UserDB

app = FastAPI()

# создаём таблицы, если их нет
Base.metadata.create_all(bind=engine)

# зависимость получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic-схемы
class UserCreate(BaseModel):
    username: str
    age: int
    city: str

class User(BaseModel):
    id: str
    username: str
    age: int
    city: str
    token: str

# POST /users — создать пользователя
@app.post("/users", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = UserDB(
        id=str(uuid4()),
        username=user.username,
        age=user.age,
        city=user.city,
        token=str(uuid4())
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# GET /userslist — получить список пользователей
@app.get("/userslist", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()
    return users
