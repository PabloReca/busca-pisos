from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

# Use psycopg3 driver (psycopg)
db_url = (
    DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
    if DATABASE_URL
    else None
)
engine = create_engine(db_url) if db_url else None
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    """Create tables if they don't exist"""
    from app.models.listing import Listing  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
