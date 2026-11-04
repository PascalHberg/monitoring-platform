from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./monitoring.db"

# connect_args={"check_same_thread": False} ist nur für SQLite notwendig
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency für FastAPI Endpoint Requests"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()