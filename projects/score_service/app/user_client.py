import httpx

USER_SERVICE_URL = "http://user-service:8000"

def get_user(user_id):
    try:
        response = httpx.get(f"{USER_SERVICE_URL}/users/{user_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except httpx.RequestError:
        return None
