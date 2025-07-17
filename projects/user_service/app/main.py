from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from typing import List
from uuid import UUID
from jose import jwt, JWTError
from datetime import datetime, timedelta

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
    # Log received data
    print("Received login data:", user_data)

    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    print("User found in database:", user)

    # If user doesn't exist — return 401 Unauthorized
    if not user:
        print("User not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check password validity
    is_password_valid = pwd_context.verify(user_data.password, user.hashed_password)
    print("Password is valid:", is_password_valid)

    if not is_password_valid:
        print("Invalid password")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    token = create_jwt(user.id)
    print("Generated token:", token)

    return {"access_token": token, "token_type": "bearer"}


@app.get("/users", response_model=List[UserListOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app.get("/users/{user_id}", include_in_schema=False) #This endpoint is hidden from Swagger but may be used in future internal services (e.g. audit or admin tools)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user.id),
        "username": user.username,
        "city": user.city
    }
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_jwt(user_id: str):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@app.get("/user/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email
    }
