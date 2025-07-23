import os
import asyncio
import json
from aiokafka import AIOKafkaConsumer
from mongo_client import db
import logging

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
logger = logging.getLogger("analytics_consumer")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler() 
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

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
    logger.info("Kafka consumer started and subscribed to topics: %s", KAFKA_TOPICS)
    logger.info("Waiting for Kafka messages...")
    try:
        async for msg in consumer:
            logger.info("Message received!")
            try:
                raw_value = msg.value.decode("utf-8")
                data = json.loads(raw_value)
                logger.info("Received event from topic '%s': %s", msg.topic, data)

                await db.events.insert_one(data)
                logger.info("Inserting data into MongoDB collection. DB: %s", db)
            except Exception as e:
                logger.error("Failed to process Kafka message: %s", str(e))
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")