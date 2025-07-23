from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import requests, logging, os 
from typing import Optional
from redis_client import get_redis, get_discount_from_cache, set_discount_cache 
from datetime import datetime
from kafka_producer import publish_event, start_kafka_producer, stop_kafka_producer



app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login",
scopes={"read:discount": "Read access to discount info"})
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

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")



async def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # user_id
    except JWTError:
        return None

async def get_user_info(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get("http://user_service:8000/user/me", headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("User service error:", e)
    return None

async def is_user_in_top(username: str) -> bool:
    try:
        response = requests.get("http://score-service:8000/leaderboard")
        if response.status_code == 200:
            leaderboard = response.json()
            return any(entry["username"] == username for entry in leaderboard)
    except Exception as e:
        print("Score service error:", e)
    return False

@app.post("/discount", responses={
    401: {"description": "Unauthorized"},
    400: {"description": "Invalid user data"},
})
async def get_discount(token: str = Depends(oauth2_scheme)):
    redis = await get_redis() 
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_info = get_user_info(token)
    print("user_info from user_service:", user_info)
    if not user_info:
        raise HTTPException(status_code=401, detail="User info unavailable")

    age = user_info.get("age")
    username = user_info.get("username")
    user_id = user_info.get("id")
    if username is None or age is None:
        raise HTTPException(status_code=400, detail="Invalid user data")
    cached_discount = await get_discount_from_cache(redis, username)
    if cached_discount:
        return {"username": username, "discount": cached_discount}
    discount = 0.0
    if age >= 40:
        discount += 0.1
    if is_user_in_top(username):
        discount += 0.1

    await redis.set(f"discount:{username}", discount, ex=3600)
    await publish_event("discount.calculated", {
        "user_id": str(user_id),
        "discount": discount,
        "timestamp": str(datetime.utcnow())
    })

    return {"username": username, "discount": round(discount, 2)}
    
