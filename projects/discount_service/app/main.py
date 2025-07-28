from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import requests, os 
from typing import Optional
from redis_client import get_redis, get_discount_from_cache, set_discount_cache 
from datetime import datetime
from kafka_producer import publish_event, start_kafka_producer, stop_kafka_producer
from logger_config import setup_logger



app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login",
scopes={"read:discount": "Read access to discount info"})
logger = setup_logger("discount_service")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")



@app.on_event("startup")
async def on_startup():
    logger.info({"event": "startup", "message": "App is starting up..."})
    await start_kafka_producer()

@app.on_event("shutdown")
async def on_shutdown():
    logger.info({"event": "shutdown", "message": "App is shutting down..."})
    await stop_kafka_producer()

async def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info({"event": "decode_token_success", "user_id": payload.get("sub")})
        return payload.get("sub")
    except JWTError as e:
        logger.warning({"event": "decode_token_fail", "error": str(e)})
        return None

async def get_user_info(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get("http://user_service:8000/user/me", headers=headers)
        if response.status_code == 200:
            logger.info({"event": "get_user_info_success", "token": token})
            return response.json()
        logger.warning({"event": "get_user_info_fail", "status_code": response.status_code})
    except Exception as e:
        logger.error({"event": "get_user_info_error", "error": str(e)})
    return None

async def is_user_in_top(username: str) -> bool:
    try:
        response = requests.get("http://score-service:8000/leaderboard")
        if response.status_code == 200:
            leaderboard = response.json()
            in_top = any(entry["username"] == username for entry in leaderboard)
            logger.info({"event": "is_user_in_top", "username": username, "in_top": in_top})
            return in_top
        logger.warning({"event": "leaderboard_request_fail", "status_code": response.status_code})
    except Exception as e:
        logger.error({"event": "leaderboard_request_error", "error": str(e)})
    return False

@app.post("/discount", responses={
    401: {"description": "Unauthorized"},
    400: {"description": "Invalid user data"},
})
async def get_discount(token: str = Depends(oauth2_scheme)):
    logger.info({"event": "discount_request", "token": token})
    redis = await get_redis()

    user_id = await decode_token(token)
    if not user_id:
        logger.warning({"event": "discount_invalid_token", "token": token})
        raise HTTPException(status_code=401, detail="Invalid token")

    user_info = await get_user_info(token)
    logger.info({"event": "user_info_received", "user_info": user_info})
    if not user_info:
        logger.warning({"event": "discount_user_info_unavailable", "token": token})
        raise HTTPException(status_code=401, detail="User info unavailable")

    age = user_info.get("age")
    username = user_info.get("username")
    user_id = user_info.get("id")

    if username is None or age is None:
        logger.warning({"event": "discount_invalid_user_data", "user_info": user_info})
        raise HTTPException(status_code=400, detail="Invalid user data")

    cached_discount = await get_discount_from_cache(redis, username)
    if cached_discount:
        logger.info({"event": "discount_cache_return", "username": username, "discount": cached_discount})
        return {"username": username, "discount": cached_discount}

    discount = 0.0
    if age >= 40:
        discount += 0.1
    if await is_user_in_top(username):
        discount += 0.1

    await set_discount_cache(redis, username, discount, ttl=3600)

    await publish_event("discount.calculated", {
        "user_id": str(user_id),
        "username": username,
        "discount": discount,
        "timestamp": str(datetime.utcnow())
    })

    logger.info({"event": "discount_calculated", "username": username, "discount": discount})
    return {"username": username, "discount": round(discount, 2)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "discount_service"}

@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    logger.info({
        "event": "http_request",
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
    })
    response = await call_next(request)
    logger.info({
        "event": "http_response",
        "status_code": response.status_code,
        "url": str(request.url),
    })
    return response
