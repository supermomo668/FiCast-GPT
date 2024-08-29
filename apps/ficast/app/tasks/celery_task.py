from celery import Celery, shared_task

# Celery Tasks
@shared_task(bind=True)
def create_podcast_task(self, task_id, podcast_request):
    task = Task(db=get_db())
    task._execute_create_podcast_task(podcast_request)

@shared_task(bind=True)
def generate_audio_task(self, task_id):
    task = Task(db=get_db())
    task._execute_generate_audio_task()