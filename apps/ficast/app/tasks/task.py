import json, uuid, os
from celery import Celery, shared_task

from fastapi import HTTPException
from sqlalchemy.orm import Session
from apps.ficast.app.models.request import PodcastRequest
from ficast.conversation.podcast import Podcast as FiCastPodcast
from ficast.character.podcast import Podcaster
from ficast.assembly.ficast import FiCast
from ficast.dialogue.speech import DialogueSynthesis

from ..logger import logger, log_error, log_info
from ..models.db import PodcastTask
from ..models.session import ScopedSession, get_db
from ..models.task_status import TaskStatus

USE_CELERY = os.getenv("USE_CELERY", "false").lower() in ("true", "1")

if USE_CELERY:
    # Optional: Create Celery app if needed
    from .celery import create_celery
    celery_app = create_celery()
else:
    import threading

class Task:
    def __init__(self, db: Session, task_id: str = None):
        self.db = db
        self.error_message = None
        if not task_id:
            self.task_id = str(uuid.uuid4())
        else:
            self.task_id = task_id
        self.thread = None
        log_info(f"Task ID: {self.task_id}")

    def create_podcast(self, podcast_request: PodcastRequest):
        try:
            # Save initial task status
            new_task = PodcastTask(
                task_id=self.task_id,
                script_status=TaskStatus.PENDING,
                audio_status=TaskStatus.PENDING,
                error_message=None
            )
            self.db.add(new_task)
            self.db.commit()

            if USE_CELERY:
                create_podcast_task.apply_async(
                    args=[self.task_id, podcast_request.model_dump()])
            else:
                self.thread = threading.Thread(
                    target=self._execute_create_podcast_task,
                    args=(podcast_request,),
                    daemon=True
                )
                self.thread.start()

            return {
                "task_id": self.task_id, 
                "status": TaskStatus.PENDING
            }

        except Exception as e:
            self._save_error(f"Failed to create podcast task: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create podcast task: {str(e)}")

    def generate_audio(self):
        try:
            # Check that script is already generated
            podcast_task = self.db.query(PodcastTask).filter(
                PodcastTask.task_id == self.task_id).first()
            if not podcast_task:
                raise ValueError("Podcast task not found")

            if podcast_task.script_status != TaskStatus.SUCCESS or not podcast_task.script:
                raise ValueError("Script must be successfully generated before audio can be created")

            if USE_CELERY:
                generate_audio_task.apply_async(args=[self.task_id])
            else:
                self.thread = threading.Thread(
                    target=self._execute_generate_audio_task,
                    daemon=True
                )
                self.thread.start()

            return {
                "task_id": self.task_id, "status": TaskStatus.PENDING
            }

        except Exception as e:
            self._save_error(f"Failed to enqueue audio task: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to enqueue audio task")

    def _execute_create_podcast_task(self, podcast_request: PodcastRequest):
        local_session = ScopedSession()
        try:
            self._update_task_status(
                self.task_id, TaskStatus.STARTED, session=local_session)

            # Create the Podcast object
            my_podcast = FiCastPodcast(
                topic=podcast_request.topic,
                n_rounds=podcast_request.n_rounds
            )

            # Add participants
            for participant in podcast_request.participants:
                podcaster = Podcaster(
                    name=participant.name,
                    description=participant.description,
                    model=participant.model,
                    role=participant.role if participant.role else "guest"
                )
                my_podcast.add([podcaster])

            # Generate script
            chat_history = my_podcast.create()

            podcast_task = local_session.query(PodcastTask).filter(
                PodcastTask.task_id == self.task_id).first()
            if not podcast_task:
                raise ValueError("Podcast task not found")
            podcast_task.script = my_podcast.json_script
            podcast_task.script_status = TaskStatus.SUCCESS
            podcast_task.chat_history = chat_history
            local_session.commit()

        except Exception as e:
            log_error(f"Failed to create podcast: {e}")
            self._save_error(f"Failed to create podcast: {str(e)}", session=local_session)
            local_session.rollback()
        finally:
            ScopedSession.remove()

    def _execute_generate_audio_task(self):
        local_session = ScopedSession()
        try:
            self._update_task_status(self.task_id, TaskStatus.STARTED, is_audio=True, session=local_session)

            podcast_task = local_session.query(PodcastTask).filter(
                PodcastTask.task_id == self.task_id).first()
            if not podcast_task:
                raise ValueError("Podcast task not found")

            # Reconstruct the podcast object from the chat history
            my_podcast = FiCastPodcast.from_chat_history(podcast_task.chat_history)

            # Synthesize dialogue to create audio
            dialoguer = DialogueSynthesis(
                client_type="api",
                base_url=os.getenv("TTS_API_BASE_URL"),
                api_key=os.getenv("TTS_API_KEY")
            )
            ficast = FiCast(conversation=my_podcast, dialogue_synthesizer=dialoguer)
            my_audio = ficast.to_podcast(ignore_errors=True)

            podcast_task.audio = my_audio
            podcast_task.audio_status = TaskStatus.SUCCESS
            local_session.commit()

        except Exception as e:
            log_error(f"Failed to generate audio: {e}")
            self._save_error(f"Failed to generate audio: {str(e)}", session=local_session)
            local_session.rollback()
        finally:
            ScopedSession.remove()

    def _save_error(self, error_message: str, session: Session = None):
        if session is None:
            session = self.db
        try:
            task = session.query(PodcastTask).filter(PodcastTask.task_id == self.task_id).first()
            if not task:
                log_error(f"Task {self.task_id} not found while trying to save error: {error_message}")
                return
            task.error_message = error_message
            task.script_status = TaskStatus.FAILURE
            task.audio_status = TaskStatus.FAILURE
            session.commit()
        except Exception as e:
            log_error(f"Failed to save error to task {self.task_id}: {e}")
            session.rollback()

    def _update_task_status(self, task_id: str, status: TaskStatus, is_audio: bool = False, session: Session = None):
        if session is None:
            session = self.db
        try:
            task = session.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
            if not task:
                raise ValueError(f"Task {task_id} not found")
            if is_audio:
                task.audio_status = status
            else:
                task.script_status = status
            session.commit()
        except Exception as e:
            self._save_error(f"Failed to update task status: {str(e)}", session=session)
            session.rollback()
    
    def _save_error(self, error_message: str, session: Session = None):
        if session is None:
            session = self.db
        try:
            task = session.query(PodcastTask).filter(PodcastTask.task_id == self.task_id).first()
            if not task:
                log_error(f"Task {self.task_id} not found while trying to save error: {error_message}")
                return
            task.error_message = error_message
            task.script_status = TaskStatus.FAILURE
            task.audio_status = TaskStatus.FAILURE
            session.commit()
        except Exception as e:
            log_error(f"Failed to save error to task {self.task_id}: {e}")
            session.rollback()
             
@shared_task(bind=True)
def create_podcast_task(self, task_id, podcast_request):
    db_session = ScopedSession()  # Create a new session for the Celery task
    try:
        task = Task(db=db_session, task_id=task_id)
        task._execute_create_podcast_task(podcast_request)
    finally:
        ScopedSession.remove()  # Clean up session

@shared_task(bind=True)
def generate_audio_task(self, task_id):
    db_session = ScopedSession()  # Create a new session for the Celery task
    try:
        task = Task(db=db_session, task_id=task_id)
        task._execute_generate_audio_task()
    finally:
        ScopedSession.remove()  # Clean up session