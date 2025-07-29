from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://userpostgres:userpassword@userdb:5432/userdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

try:
    with engine.connect() as connection:
        print(" Successful connection to userdb.")
except OperationalError as e:
    print(f" Connection error: {e}")
    raise
