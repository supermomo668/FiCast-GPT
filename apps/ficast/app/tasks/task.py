import json, uuid, os
from celery import shared_task
from fastapi import HTTPException
from sqlalchemy.orm import Session
from prometheus_client import Counter

from ficast.conversation.podcast import Podcast as FiCastPodcast
from ficast.character.podcast import Podcaster
from ficast.assembly.ficast import FiCast
from ficast.dialogue.speech import DialogueSynthesis

from ..logger import logger, log_error, log_info
from ..models.db import PodcastTask
from ..models.request import PodcastRequest
from ..models.session import ScopedSession, get_db
from ..models.task_status import TaskStatus, TaskStatusUpdate

USE_CELERY = os.getenv("USE_CELERY", "false").lower() in ("true", "1")

if USE_CELERY:
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

    def create_podcast(
        self, podcast_request: PodcastRequest
        ) -> TaskStatusUpdate:
        log_info(f"Task {self.task_id}: Starting podcast creation with {len(podcast_request.participants)} participants.")
        try:
            # Save initial task status as 'PENDING'
            new_task = PodcastTask(
                task_id=self.task_id,
                script_status=TaskStatus.PENDING,
                audio_status=TaskStatus.PENDING,
                error_message=None
            )
            self.db.add(new_task)
            self.db.commit()

            # Immediately update status to 'STARTED'
            self._update_task_status(self.task_id, TaskStatus.STARTED)

            if USE_CELERY:
                # Commit the task to the database before enqueuing the Celery task
                self.db.commit()
                # Enqueue Celery task
                create_podcast_task.apply_async(
                    args=[self.task_id, podcast_request.model_dump()])
            else:
                self.thread = threading.Thread(
                    target=self._execute_create_podcast_task,
                    args=(podcast_request,),
                    daemon=True
                )
                self.thread.start()

            return TaskStatusUpdate(
                task_id=self.task_id, 
                status=TaskStatus.STARTED
            )

        except Exception as e:
            self._save_error(f"Failed to create podcast task: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create podcast task: {str(e)}")

    def generate_audio(self) -> TaskStatusUpdate:
        try:
            # Check that script is already generated
            podcast_task = self.db.query(PodcastTask).filter(
                PodcastTask.task_id == self.task_id).first()
            if not podcast_task:
                raise ValueError("Podcast task not found")

            if podcast_task.script_status != TaskStatus.SCRIPT_CREATED or not podcast_task.script:
                raise ValueError("Script must be successfully generated before audio can be created")

            # Update task status to GENERATING_AUDIO
            self._update_task_status(
                self.task_id, TaskStatus.GENERATING_AUDIO, is_audio=True
            )

            if USE_CELERY:
                generate_audio_task.apply_async(args=[self.task_id])
            else:
                self.thread = threading.Thread(
                    target=self._execute_generate_audio_task,
                    daemon=True
                )
                self.thread.start()

            return TaskStatusUpdate(
                task_id=self.task_id, 
                status=TaskStatus.GENERATING_AUDIO
            )

        except Exception as e:
            self._save_error(f"Failed to enqueue audio task: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to enqueue audio task")

    def _execute_create_podcast_task(
        self, podcast_request: PodcastRequest
        ) -> None:
        log_info(f"Opening new session for task {self.task_id}")
        local_session = ScopedSession()
        try:
            # Update task status to indicate script generation has started
            self._update_task_status(
                self.task_id, 
                TaskStatus.GENERATING_SCRIPT, 
                session=local_session
            )

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

            # Update task status and save the generated script
            podcast_task = local_session.query(PodcastTask).filter(
                PodcastTask.task_id == self.task_id).first()

            if not podcast_task:
                raise ValueError(f"Podcast task {self.task_id} not found")

            podcast_task.script = my_podcast.json_script
            podcast_task.chat_history = chat_history
            podcast_task.script_status = TaskStatus.SCRIPT_CREATED
            local_session.commit()

        except Exception as e:
            log_error(f"Failed to create podcast: {e}")
            self._save_error(f"Failed to create podcast: {str(e)}", session=local_session)
            local_session.rollback()
            raise  # Reraise the exception to allow Celery to handle it properly

        finally:
            log_info(f"Closing session for task {self.task_id} closed")
            ScopedSession.remove()

    def _execute_generate_audio_task(self) -> None:
        local_session = ScopedSession()
        try:
            self._update_task_status(self.task_id, TaskStatus.GENERATING_AUDIO, is_audio=True, session=local_session)

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

            # Update task status to AUDIO_CREATED
            podcast_task.audio = my_audio
            podcast_task.audio_status = TaskStatus.AUDIO_CREATED
            local_session.commit()

        except Exception as e:
            log_error(f"Failed to generate audio: {e}")
            self._save_error(f"Failed to generate audio: {str(e)}", session=local_session)
            local_session.rollback()
            raise  # Reraise the exception to allow Celery to handle it properly
        finally:
            ScopedSession.remove()

    def _save_error(
        self, 
        error_message: str, session: Session = None
        ) -> None:
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

    def _update_task_status(
        self, 
        task_id: str, status: TaskStatus,
        is_audio: bool = False, session: Session = None, 
        ) -> None:
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


@shared_task(bind=True, max_retries=3)
def create_podcast_task(self, task_id, podcast_request: dict):
    db_session = ScopedSession()
    try:
        task = Task(db=db_session, task_id=task_id)
        task._execute_create_podcast_task(
            PodcastRequest(**podcast_request))
    except Exception as e:
        log_error(f"Retry {self.request.retries} for task {task_id} failed: {e}")
        self.retry(exc=e)

@shared_task(bind=True)
def generate_audio_task(self, task_id) -> None:
    db_session = ScopedSession()  # Create a new session for the Celery task
    try:
        task = Task(db=db_session, task_id=task_id)
        task._execute_generate_audio_task()
    except Exception as e:
        log_error(f"Failed to execute Celery audio task for {task_id}: {e}")
        raise  # Let Celery mark this task as failed and retry if needed
    finally:
        ScopedSession.remove()  # Clean up session
