from fastapi import FastAPI
from contextlib import asynccontextmanager
import dotenv, os

from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

dotenv.load_dotenv(".env", override=True)

from .routes import podcast, auth, basic, samples
from .models.session import init_db

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database and create tables
    init_db()
    yield
    # Cleanup resources if needed

app.include_router(auth.router)
app.include_router(samples.router)
app.include_router(basic.router)
app.include_router(podcast.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=os.getenv("ALLOWED_HEADERS", "*").split(","),
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, host="0.0.0.0", port=42110)
