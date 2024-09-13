import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Load environment variables
load_dotenv(override=True)

# Initialize the engine
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the environment variables.")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False})

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
    # Debugging print to verify model import
    print("Model imported:", PodcastTask.__tablename__)
    try:
        print(f"Initializing database with URL: {DATABASE_URL}")
        Base.metadata.create_all(bind=engine)  # Create all tables
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error during table creation: {e}")
    
if __name__ == "__main__":
  # Initialize the database entrypoint (manual)
  init_db()