# kafka_producer.py
import os
import json
from datetime import datetime
from aiokafka import AIOKafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
_producer = None

async def start_kafka_producer():
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await _producer.start()

async def publish_event(topic: str, data: dict):
    if _producer is None:
        raise RuntimeError("Kafka producer not initialized")
    data["timestamp"] = str(datetime.utcnow())
    await _producer.send_and_wait(topic, data)

async def stop_kafka_producer():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
