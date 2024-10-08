from venv import logger
from fastapi import FastAPI
from contextlib import asynccontextmanager
import dotenv, os

from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

dotenv.load_dotenv(".env")

from .routes import podcast, auth, basic, samples
from .models.session import init_db
from .constants import API_DOC, API_REDOC, APP_ROOT

if os.getenv("TEST_USERS"):
    logger.info(f"Enabled test users only mode. Only the following users will be able to access protected API:{os.getenv('TEST_USERS')}")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the sqlite and create tables
    init_db()
    yield

# Pass the lifespan context manager to FastAPI
app = FastAPI(
    title="LoFi Podcast API",
    docs_url=API_DOC,
    redoc_url=API_REDOC,
    root_path=APP_ROOT,
    lifespan=lifespan  # Provide the lifespan function here
)

# Include your routers
app.include_router(auth.router)
app.include_router(samples.router)
app.include_router(basic.router)
app.include_router(podcast.router)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "localhost,127.0.0.1").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=os.getenv("ALLOWED_HEADERS", "*").split(","),
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")
)

# Run the application with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=42110)
