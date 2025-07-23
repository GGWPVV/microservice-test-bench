import asyncio
from kafka_consumer import consume 
import socket
from logger_config import setup_logger

logger = setup_logger("analytics_service")

async def wait_for_kafka(host: str, port: int, timeout=60):
    start = asyncio.get_event_loop().time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info({"event": "kafka_available", "host": host, "port": port})
                return
        except OSError:
            now = asyncio.get_event_loop().time()
            if now - start > timeout:
                logger.error({"event": "kafka_timeout", "host": host, "port": port, "timeout": timeout})
                raise TimeoutError(f"Could not connect to Kafka at {host}:{port} after {timeout}s")
            logger.info({"event": "kafka_wait", "host": host, "port": port})
            await asyncio.sleep(2)

async def main():
    logger.info({"event": "service_start", "message": "Analytics service starting..."})
    await wait_for_kafka("kafka", 9092, timeout=60)
    await consume()

if __name__ == "__main__":
    logger.info({"event": "main_run", "message": "Running analytics main loop"})
    asyncio.run(main())
