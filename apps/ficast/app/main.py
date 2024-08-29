from fastapi import FastAPI
from contextlib import asynccontextmanager
import dotenv

dotenv.load_dotenv(".env", override=True)

from .routes import podcast, auth, basic
from .utils import create_celery
from .models.session import init_db

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database and create tables
    init_db()
    yield
    # Cleanup resources if needed
    
app.include_router(auth.router)
app.include_router(basic.router)
app.include_router(podcast.router)

# Optional: Create Celery app if needed
celery = create_celery(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, host="0.0.0.0", port=42110)
