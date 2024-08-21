from celery import Celery
from .models import PodcastRequest

celery = Celery(__name__)

@celery.task
def generate_audio_task(request_data: dict):
    # Simulate generating podcast audio
    podcast_request = PodcastRequest(**request_data)
    # Integration with AI library goes here
    return f"Generated audio for podcast on {podcast_request.topic}"
