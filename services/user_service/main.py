from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from uuid import uuid4

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    age: int
    city: str

class User(UserCreate):
    id: str
    token: str

users: List[User] = []

@app.post("/users")
def create_user(user: UserCreate):
    new_user = User(**user.dict(), id=str(uuid4()), token=str(uuid4()))
    users.append(new_user)
    return new_user
