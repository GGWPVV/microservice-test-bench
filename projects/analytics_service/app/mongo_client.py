import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongouser:mongopass@mongo:27017/?authSource=admin"
)
MONGO_DB = os.getenv("MONGO_DB", "analytics_db")

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[MONGO_DB]