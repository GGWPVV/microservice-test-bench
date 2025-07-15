from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
import uuid
from database import Base
from pydantic import BaseModel

# SQLAlchemy модель для базы
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    city = Column(String, nullable=False)
    age = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic схема для создания пользователя
class UserCreate(BaseModel):
    username: str
    password: str
    age: int
    city: str

# Pydantic схема для ответа пользователем
class UserOut(BaseModel):
    username: str
    age: int
    city: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class UserListOut(BaseModel):
    username: str
    age: int
    city: str

    class Config:
        orm_mode = True
