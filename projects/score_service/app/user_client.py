import requests
import os
def get_user(token: str):
    if not token.startswith("Bearer "):
        token = f"Bearer {token}"  # Ensure the token starts with "Bearer "

    headers = {"Authorization": token}
    try:
        response = requests.get("http://user_service:8000/user/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        print("User service response:", response.status_code, response.text)
        return None
    except requests.exceptions.RequestException as e:
        print("Error contacting user service:", e)
        return None

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
