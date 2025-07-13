from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from typing import List

from database import SessionLocal, engine, Base
import models
from models import UserCreate, UserOut, UserLogin, User, UserListOut

# создаём таблицы, если их ещё нет
Base.metadata.create_all(bind=engine)

app = FastAPI()

# включаем CORS (если надо)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST /users — регистрация нового пользователя
@app.post("/users", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        city=user.city,
        age=user.age,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_name": str(new_user.username)}

# POST /login — авторизация
@app.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "user_id": str(user.id)}
@app.get("/users", response_model=List[UserListOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

