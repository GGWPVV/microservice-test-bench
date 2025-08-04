import os
import json
import asyncio
from datetime import datetime
from aiokafka import AIOKafkaProducer
from shared.logger_config import setup_logger

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
_producer = None
logger = setup_logger("kafka_client")

async def start_kafka_producer(retries: int = 10, delay: int = 5):
    global _producer
    if _producer is None:
        logger.info({"event": "kafka_start", "message": "Starting Kafka producer..."})
        for attempt in range(retries):
            try:
                _producer = AIOKafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8")
                )
                await _producer.start()
                logger.info({"event": "kafka_started", "message": "Kafka producer started"})
                return
            except Exception as e:
                logger.warning({
                    "event": "kafka_retry",
                    "attempt": attempt + 1,
                    "error": str(e),
                    "message": "Kafka not ready yet"
                })
                await asyncio.sleep(delay)
        logger.error({"event": "kafka_fail", "message": "Kafka producer could not be started after retries, continuing without Kafka"})
        _producer = None

async def publish_event(topic: str, data: dict):
    if _producer is None:
        logger.warning({"event": "publish_event", "message": "Kafka producer not initialized, skipping event"})
        return None
    try:
        data["timestamp"] = str(datetime.utcnow())
        result = await _producer.send_and_wait(topic, data)
        logger.info({
            "event": "kafka_publish",
            "topic": topic,
            "data": data,
            "message": f"Message sent to Kafka topic '{topic}'"
        })
        return result
    except Exception as e:
        logger.error({
            "event": "kafka_publish_error",
            "topic": topic,
            "data": data,
            "error": str(e),
            "message": "Failed to publish event to Kafka"
        }, exc_info=True)

async def stop_kafka_producer():
    global _producer
    if _producer:
        logger.info({"event": "kafka_stop", "message": "Stopping Kafka producer..."})
        await _producer.stop()
        _producer = None
        logger.info({"event": "kafka_stopped", "message": "Kafka producer stopped"})