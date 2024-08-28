import os

# In-memory storage for podcast objects
podcast_store = {}
audio_store = {}

USE_CELERY = os.getenv("USE_CELERY", "false").lower() == "true"