from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
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
