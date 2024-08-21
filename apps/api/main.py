from fastapi import FastAPI
from .routes import podcast, auth
from .utils import create_celery

app = FastAPI()

app.include_router(podcast.router)
app.include_router(auth.router)

# Optional: Create Celery app if needed
celery = create_celery(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=42110)
