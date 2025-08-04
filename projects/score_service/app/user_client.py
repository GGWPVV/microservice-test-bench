import requests
import os
from shared.logger_config import setup_logger

logger = setup_logger("user_client")

def get_user(token: str):
    if not token.startswith("Bearer "):
        token = f"Bearer {token}"  # Ensure the token starts with "Bearer "

    headers = {"Authorization": token}
    try:
        response = requests.get("http://user_service:8000/user/me", headers=headers)
        if response.status_code == 200:
            logger.info({"event": "get_user_success", "token": token})
            return response.json()
        logger.warning({"event": "get_user_fail", "status_code": response.status_code, "response": response.text})
        return None
    except requests.exceptions.RequestException as e:
        logger.error({"event": "get_user_error", "error": str(e)})
        return None

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
