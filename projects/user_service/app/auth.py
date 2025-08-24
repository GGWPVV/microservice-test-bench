from jose import jwt
from datetime import datetime, timedelta, timezone
from shared.logger_config import setup_logger

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

logger = setup_logger("auth")

def create_jwt(user_id):
    try:
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        logger.info({
            "event": "jwt_created",
            "user_id": str(user_id),
            "message": "JWT token created"
        })
        return token
    except Exception as e:
        logger.error({
            "event": "jwt_create_error",
            "user_id": str(user_id),
            "error": str(e),
            "message": "Error creating JWT token"
        }, exc_info=True)
        raise

