from fastapi import FastAPI
import uvicorn
import asyncio
from datetime import datetime
from kafka_consumer import consume
from schemas import HealthResponse

app = FastAPI(
    title="Analytics Service API",
    description="Microservice for analytics and event processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Check service health status",
    responses={
        200: {
            "description": "Service is healthy",
            "model": HealthResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "analytics_service",
                        "timestamp": "2025-01-01T12:00:00Z"
                    }
                }
            }
        }
    }
)
async def health_check():
    return {
        "status": "healthy", 
        "service": "analytics_service",
        "timestamp": datetime.utcnow().isoformat()
    }

async def start_services():
    # Start Kafka consumer in background
    consumer_task = asyncio.create_task(consume())
    
    # Start HTTP server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_services())