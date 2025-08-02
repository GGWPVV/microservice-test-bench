from fastapi import FastAPI, HTTPException, Depends , Request
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Annotated
from uuid import UUID
from jose import jwt, JWTError
from datetime import datetime, timedelta
from shared.logger_config import setup_logger

from database import SessionLocal, engine, Base
import models
from models import User
from schemas import (
    UserCreate, UserCreateResponse, UserLogin, TokenResponse, 
    UserListOut, CurrentUserResponse, ErrorResponse, 
    ValidationErrorResponse, InternalErrorResponse, HealthResponse
)
from shared.kafka_client import publish_event, start_kafka_producer, stop_kafka_producer

# Base.metadata.create_all(bind=engine)  # Use migrations instead

app = FastAPI(
    title="User Service API",
    description="Microservice for user management with authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger = setup_logger("user_service")  

@app.on_event("startup")
async def on_startup():
    logger.info({"event": "startup", "message": "App is starting up..."})
    await start_kafka_producer()

@app.on_event("shutdown")
async def on_shutdown():
    logger.info({"event": "shutdown", "message": "App is shutting down..."})
    await stop_kafka_producer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", 
    status_code=201, 
    response_model=UserCreateResponse,
    tags=["Users"],
    summary="Create new user",
    description="Register a new user in the system",
    responses={
        201: {
            "description": "User created successfully",
            "model": UserCreateResponse,
            "content": {
                "application/json": {
                    "example": {
                        "message": "User created successfully",
                        "user_name": "john_doe"
                    }
                }
            }
        },
        409: {
            "description": "Conflict - User already exists",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate_username": {
                            "summary": "Username already exists",
                            "value": {"detail": "Username already exists"}
                        },
                        "duplicate_email": {
                            "summary": "Email already exists", 
                            "value": {"detail": "Email already exists"}
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "model": ValidationErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            },
                            {
                                "loc": ["body", "age"],
                                "msg": "ensure this value is greater than or equal to 13",
                                "type": "value_error.number.not_ge"
                            }
                        ]
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
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info({
        "event": "create_user_request",
        "username": user.username,
        "email": user.email,
        "message": "Registering new user"
    })
    try:
        hashed_password = pwd_context.hash(user.password)
        new_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            city=user.city,
            age=user.age,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        await publish_event("user.registered", {
            "user_id": str(new_user.id),
            "username": new_user.username,
            "timestamp": str(datetime.utcnow())
        })
        logger.info({
            "event": "user_created",
            "user_id": str(new_user.id),
            "username": new_user.username,
            "message": "User created successfully"
        })
        return {"message": "User created successfully", "user_name": new_user.username}
    except Exception as e:
        db.rollback()
        error_str = str(e).lower()
        
        # Handle unique constraint violations
        if "unique constraint" in error_str or "duplicate key" in error_str:
            if "username" in error_str:
                logger.warning({
                    "event": "duplicate_username",
                    "username": user.username,
                    "message": "Username already exists"
                })
                raise HTTPException(status_code=409, detail="Username already exists")
            elif "email" in error_str:
                logger.warning({
                    "event": "duplicate_email",
                    "email": user.email,
                    "message": "Email already exists"
                })
                raise HTTPException(status_code=409, detail="Email already exists")
            else:
                logger.warning({
                    "event": "duplicate_user_data",
                    "username": user.username,
                    "email": user.email,
                    "message": "User with this data already exists"
                })
                raise HTTPException(status_code=409, detail="User already exists")
        
        # Handle other database errors
        logger.error({
            "event": "user_create_error",
            "username": user.username,
            "email": user.email,
            "error": str(e),
            "message": "Error creating user"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

from auth import create_jwt

@app.post("/login",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="User login",
    description="Authenticate user and return JWT token",
    responses={
        200: {
            "description": "Login successful",
            "model": TokenResponse,
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmZGYzYjEyNi04YmVjLTRjZTMtOTE5Mi1jOGE5NDRkZWU5OGIiLCJleHAiOjE3NTM3MzgyMTF9.h8c9_KIp-yPhRC0PmPfBDiNJc39tI1UtO0mSbaUY-Ug",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid credentials"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "model": ValidationErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            },
                            {
                                "loc": ["body", "password"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
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
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        logger.info({
            "event": "login_attempt",
            "email": user_data.email,
            "message": "Login attempt"
        })
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user:
            logger.warning({
                "event": "login_failed",
                "email": user_data.email,
                "message": "User not found"
            })
            raise HTTPException(status_code=401, detail="Invalid credentials")
        is_password_valid = pwd_context.verify(user_data.password, user.hashed_password)
        if not is_password_valid:
            logger.warning({
                "event": "login_failed",
                "username": user.username,
                "email": user_data.email,
                "message": "Invalid password"
            })
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_jwt(user.id)
        logger.info({
            "event": "login_success",
            "user_id": str(user.id),
            "username": user.username,
            "message": "User logged in successfully"
        })
        await publish_event("user.logged_in", {
            "user_id": str(user.id),
            "username": user.username,
            "timestamp": str(datetime.utcnow())
        })
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error({
            "event": "login_error",
            "error": str(e),
            "message": "Error during login"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users", 
    response_model=List[UserListOut],
    tags=["Users"],
    summary="Get all users",
    description="Retrieve list of all registered users",
    responses={
        200: {
            "description": "List of users retrieved successfully",
            "model": List[UserListOut],
            "content": {
                "application/json": {
                    "example": [
                        {
                            "username": "john_doe",
                            "age": 25,
                            "city": "New York"
                        },
                        {
                            "username": "jane_smith",
                            "age": 30,
                            "city": "Los Angeles"
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
def get_users(db: Session = Depends(get_db)):
    try:
        logger.info({"event": "get_users", "message": "Fetching all users"})
        users = db.query(models.User).all()
        return users
    except Exception as e:
        logger.error({
            "event": "get_users_error",
            "error": str(e),
            "message": "Error fetching users"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/{user_id}", include_in_schema=False)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    logger.info({"event": "get_user", "user_id": str(user_id), "message": "Fetching user by ID"})
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning({"event": "get_user_failed", "user_id": str(user_id), "message": "User not found"})
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user.id),
        "username": user.username,
        "city": user.city
    }

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_jwt(user_id: str):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@app.get("/user/me",
    response_model=CurrentUserResponse,
    tags=["Authentication"],
    summary="Get current user",
    description="Get current authenticated user information",
    responses={
        200: {
            "description": "Current user information",
            "model": CurrentUserResponse,
            "content": {
                "application/json": {
                    "example": {
                        "id": "fdf3b126-8bec-4ce3-9192-c8a944dee98b",
                        "username": "john_doe",
                        "age": 25
                    }
                }
            }
        },
        401: {
            "description": "Invalid or expired token",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid token"
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User not found"
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
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error({
            "event": "get_current_user_error",
            "error": str(e),
            "message": "Error processing token"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": str(user.id),
            "username": user.username,
            "age": user.age
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error({
            "event": "get_current_user_db_error",
            "user_id": user_id,
            "error": str(e),
            "message": "Database error fetching user"
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
@app.get("/health", 
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the service is healthy",
    responses={
        200: {
            "description": "Service is healthy",
            "model": HealthResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "user_service",
                        "timestamp": "2025-01-01T00:00:00Z"
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
                        "detail": "Service health check failed"
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
            "service": "user_service",
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
    logger.info({
        "event": "http_request",
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
    })
    response = await call_next(request)
    logger.info({
        "event": "http_response",
        "status_code": response.status_code,
        "url": str(request.url),
    })
    return response