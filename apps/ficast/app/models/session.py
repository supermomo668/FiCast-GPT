import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Load environment variables
load_dotenv()

# Initialize the engine
DATABASE_URL = os.getenv("DATABASE_URL")
assert DATABASE_URL, "DATABASE_URL must be set in the environment variables."

engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(SessionLocal)

def get_db():
    """Yields a database session object. This method is a context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database schema by creating all tables."""
    from .base import Base
    from .db import PodcastTask  # Ensure all models are imported here
    
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
  # Initialize the database entrypoint (manual)
  init_db()