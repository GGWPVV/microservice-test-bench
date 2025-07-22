import asyncio
from kafka_consumer import consume 
import socket

async def wait_for_kafka(host: str, port: int, timeout=60):
    start = asyncio.get_event_loop().time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"Kafka is available at {host}:{port}")
                return
        except OSError:
            now = asyncio.get_event_loop().time()
            if now - start > timeout:
                raise TimeoutError(f"Could not connect to Kafka at {host}:{port} after {timeout}s")
            print(f"Waiting for Kafka at {host}:{port}...")
            await asyncio.sleep(2)

async def main():
    await wait_for_kafka("kafka", 9092, timeout=60)
    await consume()

if __name__ == "__main__":
    asyncio.run(main())
