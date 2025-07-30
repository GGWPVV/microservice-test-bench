from fastapi import FastAPI, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
import random
from datetime import datetime
from database import get_db
from models import UserScore
import sys
sys.path.insert(0, '/shared')
from redis_client import get_redis, RedisCache
from kafka_client import publish_event
from logger_config import setup_logger
import models, database, json
from user_client import get_user
from schemas import (
    RollResponse, LeaderboardEntry, ErrorResponse, 
    AlreadyRolledError, InternalErrorResponse, HealthResponse, CacheResponse
)
from typing import List

app = FastAPI(
    title="Score Service API",
    description="Microservice for score management and leaderboards",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
# models.Base.metadata.create_all(bind=database.engine)  # Используем миграции вместо этого
from kafka_client import start_kafka_producer, stop_kafka_producer
logger = setup_logger("score_service")
http_logger = setup_logger("score_service")

@app.on_event("startup")
async def on_startup():
    logger.info({"event": "startup", "message": "App is starting up..."})
    await start_kafka_producer()

@app.on_event("shutdown")
async def on_shutdown():
    logger.info({"event": "shutdown", "message": "App is shutting down..."})
    await stop_kafka_producer()

@app.post("/roll",
    response_model=RollResponse,
    tags=["Score"],
    summary="Roll for score",
    description="Generate a random score for authenticated user",
    responses={
        200: {
            "description": "Score generated successfully",
            "model": RollResponse,
            "content": {
                "application/json": {
                    "example": {
                        "username": "john_doe",
                        "score": 750000,
                        "timestamp": "2025-01-01T12:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "User already rolled",
            "model": AlreadyRolledError,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "You have already rolled."
                    }
                }
            }
        },
        403: {
            "description": "Invalid token",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid token"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authorization header required"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": InternalErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def draw_score(
    Authorization: str = Header(...), 
    db: Session = Depends(get_db)
):
    try:
        logger.info({"event": "roll_request", "message": "Roll endpoint called", "Authorization": Authorization})
        redis = await get_redis()
        await redis.delete("leaderboard_top10")

        user_data = get_user(Authorization)
        if not user_data:
            logger.warning({"event": "invalid_token", "message": "Invalid token", "Authorization": Authorization})
            raise HTTPException(status_code=403, detail="Invalid token")

        user_id = user_data["id"]
        username = user_data["username"]

        # 2. Check if user has already rolled
        if await RedisCache.exists(f"already_rolled:{user_id}"):
            logger.info({"event": "already_rolled", "user_id": user_id, "username": username})
            raise HTTPException(status_code=400, detail="You have already rolled.")

        # 3. Generate and save score
        score_value = random.randint(1, 1_000_000)
        existing = db.query(models.UserScore).filter_by(user_id=user_id).first()
        if existing:
            logger.info({"event": "score_update", "user_id": user_id, "old_score": existing.score, "new_score": score_value})
            existing.score = score_value
            existing.created_at = datetime.utcnow()
            new_score = existing
        else: 
            logger.info({"event": "score_create", "user_id": user_id, "score": score_value})
            new_score = models.UserScore(
                user_id=user_id,
                username=username,
                score=score_value,
                created_at=datetime.utcnow()
            )
            db.add(new_score)
        db.commit()

        await publish_event("score.rolled", {
            "user_id": user_id,
            "username": username,
            "score": score_value
        })

        # 4. Flag user as having rolled
        await RedisCache.set(f"already_rolled:{user_id}", "1", ttl=60*60*24*365)

        logger.info({"event": "roll_success", "user_id": user_id, "username": username, "score": score_value})
        return {
            "username": username,
            "score": score_value,
            "timestamp": new_score.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error({
            "event": "roll_error",
            "error": str(e),
            "message": "Error during roll"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/leaderboard",
    response_model=List[LeaderboardEntry],
    tags=["Leaderboard"],
    summary="Get leaderboard",
    description="Retrieve top 10 players leaderboard",
    responses={
        200: {
            "description": "Leaderboard retrieved successfully",
            "model": List[LeaderboardEntry],
            "content": {
                "application/json": {
                    "example": [
                        {
                            "username": "john_doe",
                            "score": 950000,
                            "play_date": "2025-01-01T12:00:00Z"
                        },
                        {
                            "username": "jane_smith",
                            "score": 850000,
                            "play_date": "2025-01-01T11:30:00Z"
                        }
                    ]
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": InternalErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def get_leaderboard(
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
):
    try:
        cached = await redis.get("leaderboard_top10")
        if cached:
            logger.info({"event": "leaderboard_cache_hit"})
            return json.loads(cached)

        logger.info({"event": "leaderboard_cache_miss"})
        top_players = (
            db.query(UserScore)
            .order_by(UserScore.score.desc())
            .limit(10)
            .all()
        )

        result = [
            {
                "username": entry.username,
                "score": entry.score,
                "play_date": entry.created_at.isoformat()
            }
            for entry in top_players
        ]

        await redis.set("leaderboard_top10", json.dumps(result), ex=60)  # TTL 60s
        logger.info({"event": "leaderboard_cache_set", "count": len(result)})
        return result
    except Exception as e:
        logger.error({
            "event": "leaderboard_error",
            "error": str(e),
            "message": "Error fetching leaderboard"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/leaderboard/cache",
    response_model=CacheResponse,
    tags=["Leaderboard"],
    summary="Clear leaderboard cache",
    description="Clear cached leaderboard data",
    responses={
        200: {
            "description": "Cache cleared successfully",
            "model": CacheResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Leaderboard cache cleared"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": InternalErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def clear_leaderboard_cache(redis = Depends(get_redis)):
    try:
        await redis.delete("leaderboard_top10")
        logger.info({"event": "leaderboard_cache_cleared"})
        return {"detail": "Leaderboard cache cleared"}
    except Exception as e:
        logger.error({
            "event": "cache_clear_error",
            "error": str(e),
            "message": "Error clearing cache"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

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
                        "service": "score_service",
                        "timestamp": "2025-01-01T12:00:00Z"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": InternalErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def health_check():
    try:
        return {
            "status": "healthy", 
            "service": "score_service",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error({
            "event": "health_check_error",
            "error": str(e),
            "message": "Health check failed"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    http_logger.info({
        "event": "http_request",
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
    })
    response = await call_next(request)
    http_logger.info({
        "event": "http_response",
        "status_code": response.status_code,
        "url": str(request.url),
    })
    return response
