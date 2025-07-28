import os
import asyncio
import json
from aiokafka import AIOKafkaConsumer
from mongo_client import db
import sys
sys.path.insert(0, '/shared')
from logger_config import setup_logger

logger = setup_logger("analytics_service")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

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
    logger.info({"event": "kafka_consumer_started", "topics": KAFKA_TOPICS})
    logger.info({"event": "kafka_waiting", "message": "Waiting for Kafka messages..."})
    try:
        async for msg in consumer:
            logger.info({"event": "kafka_message_received", "topic": msg.topic})
            try:
                raw_value = msg.value.decode("utf-8")
                data = json.loads(raw_value)
                logger.info({"event": "event_received", "topic": msg.topic, "data": data})

                await db.events.insert_one(data)
                logger.info({"event": "mongo_insert", "db": str(db), "collection": "events"})
            except Exception as e:
                logger.error({"event": "process_error", "error": str(e)})
    finally:
        await consumer.stop()
        logger.info({"event": "kafka_consumer_stopped"})