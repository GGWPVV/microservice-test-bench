import httpx

USER_SERVICE_URL = "http://user-service:8000"

def get_user(token: str):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = httpx.get(f"{USER_SERVICE_URL}/user/me", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"User service error: {response.status_code}, {response.text}")
            return None
    except httpx.RequestError as e:
        print(f"Request to user service failed: {e}")
        return None
