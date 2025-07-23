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
import models, logging
from models import UserCreate, UserCreateResponse, UserLogin, User, UserListOut
from kafka_producer import publish_event, start_kafka_producer, stop_kafka_producer

# создаём таблицы, если их ещё нет
Base.metadata.create_all(bind=engine)

app = FastAPI()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def on_startup():
    logging.info("App is starting up...")
    await start_kafka_producer()

@app.on_event("shutdown")
async def on_shutdown():
    logging.info("App is shutting down...")
    await stop_kafka_producer()

# включаем CORS (если надо)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# for OAuth2
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    # POST /users - create new user
@app.post("/users", status_code=201, response_model=UserCreateResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info("Registering new user: %s", user.username)
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
    await publish_event("user.registered", {
        "user_id": str(new_user.id),
        "username": new_user.username,
        "timestamp": str(datetime.utcnow())
    })
    logger.info("user.registered published for %s", new_user.username)

    return {"message": "User created successfully", "user_name": new_user.username}



# POST /login — авторизация
from auth import create_jwt  # импорт функции

@app.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    print("Received login data:", user_data)
    user = db.query(User).filter(User.email == user_data.email).first()
    print("User found in database:", user)
    if not user:
        print("User not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    is_password_valid = pwd_context.verify(user_data.password, user.hashed_password)
    print("Password is valid:", is_password_valid)
    if not is_password_valid:
        print("Invalid password")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt(user.id)
    logger.info("User %s logged in successfully", user.username)
    await publish_event("user.logged_in", {
        "user_id": str(user.id),
        "username": user.username,
        "timestamp": str(datetime.utcnow())
    })
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
    print(f"Returning user info: {{'id': str(user.id), 'username': user.username, 'age': user.age}}")

    return {
        "id": str(user.id),
        "username": user.username,
        "age": user.age
    }
