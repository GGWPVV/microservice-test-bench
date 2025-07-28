from fastapi import FastAPI
import uvicorn
import asyncio
from kafka_consumer import consume

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics_service"}

async def start_services():
    # Start Kafka consumer in background
    consumer_task = asyncio.create_task(consume())
    
    # Start HTTP server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_services())