from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CityRequest(BaseModel):
    city: str

@app.post("/discount")
def get_discount(data: CityRequest):
    discount = 5 if data.city.lower() == "lisbon" else 0
    return {"discount": discount}
