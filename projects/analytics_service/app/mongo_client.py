import os
from motor.motor_asyncio import AsyncIOMotorClient
import sys
sys.path.insert(0, '/shared')
from logger_config import setup_logger

logger = setup_logger("mongo_client")

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongouser:mongopass@mongo:27017/?authSource=admin"
)
MONGO_DB = os.getenv("MONGO_DB", "analytics_db")

logger.info({"event": "mongo_connect", "uri": MONGO_URI, "db": MONGO_DB})

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[MONGO_DB]