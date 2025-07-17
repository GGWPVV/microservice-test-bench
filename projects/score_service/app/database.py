# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://scorepostgres:scorepassword@scoredb:5432/scoredb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Check connection to the database
try:
    with engine.connect() as connection:
        print("Successful connection to scoredb.")
except OperationalError as e:
    print(f"Connection error: {e}")
    raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
