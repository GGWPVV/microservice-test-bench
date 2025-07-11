from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AgeRequest(BaseModel):
    age: int

@app.post("/discount")
def get_discount(data: AgeRequest):
    discount = 10 if data.age > 35 else 0
    return {"discount": discount}
