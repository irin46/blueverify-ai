from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# The engine is the connection to the SQLite file on disk
engine = create_engine(
    settings.database_url,
    # Required for SQLite only — allows the same connection to be used
    # across multiple threads (FastAPI uses a thread pool)
    connect_args={"check_same_thread": False},
)

# Each request gets its own short-lived database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All ORM models will inherit from this Base class
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that opens a DB session for a request
    and closes it automatically when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
