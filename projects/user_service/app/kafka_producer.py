# kafka_producer.py
import os
import json
from datetime import datetime
from aiokafka import AIOKafkaProducer
import logging
import asyncio

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
_producer = None
logger = logging.getLogger(__name__)

async def start_kafka_producer(retries: int = 10, delay: int = 5):
    global _producer
    if _producer is None:
        logger.info("Starting Kafka producer...")
        for attempt in range(retries):
            try:
                _producer = AIOKafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8")
                )
                await _producer.start()
                logger.info("Kafka producer started")
                return
            except Exception as e:
                logger.warning(f"Kafka not ready yet (attempt {attempt + 1}/{retries}): {e}")
                await asyncio.sleep(delay)
        raise RuntimeError("Kafka producer could not be started after retries")


async def publish_event(topic: str, data: dict):
    if _producer is None:
        raise RuntimeError("Kafka producer not initialized")
    try:
        data["timestamp"] = str(datetime.utcnow())
        result = await _producer.send_and_wait(topic, data)
        logger.info(f"Message sent to Kafka topic '{topic}': {data}")
        return result
    except Exception as e:
        logger.exception(f"Failed to publish event to Kafka: {e}")



async def stop_kafka_producer():
    global _producer
    if _producer:
        logger.info("Stopping Kafka producer...")
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")