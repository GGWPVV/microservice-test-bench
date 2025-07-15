import jwt as PyJWT
from datetime import datetime, timedelta, timezone

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_jwt(user_id):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = PyJWT.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
