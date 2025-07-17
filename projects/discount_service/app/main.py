from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import requests
from typing import Optional
import os

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # user_id
    except JWTError:
        return None

def get_user_info(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get("http://user_service:8000/user/me", headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("User service error:", e)
    return None

def is_user_in_top(username: str) -> bool:
    try:
        response = requests.get("http://score_service:8003/leaderboard")
        if response.status_code == 200:
            leaderboard = response.json()
            return any(entry["username"] == username for entry in leaderboard)
    except Exception as e:
        print("Score service error:", e)
    return False

@app.post("/discount")
def get_discount(token: str = Depends(oauth2_scheme)):
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_info = get_user_info(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="User info unavailable")

    age = user_info.get("age")
    username = user_info.get("username")
    if username is None or age is None:
        raise HTTPException(status_code=400, detail="Invalid user data")

    discount = 0.0
    if age >= 40:
        discount += 0.1
    if is_user_in_top(username):
        discount += 0.1

    return {"username": username, "discount": round(discount, 2)}
