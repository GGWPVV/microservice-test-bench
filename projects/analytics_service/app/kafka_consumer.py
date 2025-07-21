import os
import asyncio
import json
from aiokafka import AIOKafkaConsumer
from app.mongo_client import db

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

# Topics to consume
KAFKA_TOPICS = [
    "user.registered",
    "user.logged_in",
    "score.rolled",
    "discount.calculated"
]

async def consume():
    consumer = AIOKafkaConsumer(
        *KAFKA_TOPICS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="analytics_group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))
                event_type = msg.topic
                data["event_type"] = event_type  # Add event type to data
                await db.events.insert_one(data)
                print(f"Stored event: {event_type} ->", data)
            except Exception as e:
                print(f"Failed to process message: {e}")
    finally:
        await consumer.stop()
