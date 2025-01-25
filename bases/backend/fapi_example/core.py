from fastapi import FastAPI

from backend.observability.core import print_hello_world

app = FastAPI()


@app.get("/")
async def root():
    print_hello_world()
    return {"message": "Hello World"}
