from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from typing import List
from uuid import UUID


from database import SessionLocal, engine, Base
import models
from models import UserCreate, UserCreateResponse, UserLogin, User, UserListOut

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
@app.post("/users", status_code=201, response_model=UserCreateResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    print("UserCreate:", user)
    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        city=user.city,
        age=user.age,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_name": new_user.username}


# POST /login — авторизация
from auth import create_jwt  # импорт функции

@app.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt(user.id)

    return {"access_token": token, "token_type": "bearer"}

@app.get("/users", response_model=List[UserListOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app.get("/users/{user_id}")
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user.id),
        "username": user.username,
        "city": user.city
    }
