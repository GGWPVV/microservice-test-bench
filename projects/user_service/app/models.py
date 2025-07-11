from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base
from pydantic import BaseModel

# SQLAlchemy модель для базы
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
    token = Column(UUID(as_uuid=True), default=uuid.uuid4)

# Pydantic схема для создания пользователя
class UserCreate(BaseModel):
    username: str
    age: int
    city: str

# Pydantic схема для ответа пользователем
class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    age: int
    city: str
    token: uuid.UUID

    class Config:
        orm_mode = True
