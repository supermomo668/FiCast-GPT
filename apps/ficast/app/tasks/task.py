import json, uuid, os
from celery import Celery, shared_task

from fastapi import HTTPException
from sqlalchemy.orm import Session
from apps.ficast.app.models.request import PodcastRequest
from ficast.conversation.podcast import Podcast as FiCastPodcast
from ficast.character.podcast import Podcaster
from ficast.assembly.ficast import FiCast
from ficast.dialogue.speech import DialogueSynthesis

from ..logger import logger
from ..models.db import PodcastTask
from ..models.session import SessionLocal, get_db
from ..models.task_status import TaskStatus

USE_CELERY = os.getenv("USE_CELERY", "false").lower() == "true"
if not USE_CELERY:
    import threading

class Task:
    def __init__(self, db: Session, task_id: str = None):
        self.db = db
        if not task_id:
            self.task_id = str(uuid.uuid4())
        else:
            logger.info(f"Reusing Task ID: {task_id}")
            self.task_id = task_id
        logger.info(f"Assigned Task ID: {self.task_id}")

    def create_podcast(self, podcast_request: PodcastRequest):
        try:
            # Save initial task status
            new_task = PodcastTask(
                task_id=self.task_id,
                script_status=TaskStatus.PENDING,
                audio_status=TaskStatus.PENDING
            )
            self.db.add(new_task)
            self.db.commit()

            if USE_CELERY:
                # Enqueue Celery task
                create_podcast_task.apply_async(
                    args=[self.task_id, podcast_request.model_dump()])
            else:
                # Start non-blocking async task in a separate thread
                self.thread = threading.Thread(
                    target=self._execute_create_podcast_task,
                    args=(podcast_request,),
                    daemon=True
                )
                self.thread.start()

            return {
                "task_id": self.task_id, "status": TaskStatus.PENDING
            }

        except Exception as e:
            logger.error(f"Failed to create podcast task: {e}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create podcast task")

    def generate_audio(self):
        try:
            # Use a fresh session to ensure that the PodcastTask object is not detached
            with SessionLocal() as session:
                podcast_task = session.query(PodcastTask).filter(PodcastTask.task_id == self.task_id).first()

                if not podcast_task:
                    raise ValueError("Podcast task not found")

                if podcast_task.script_status != TaskStatus.SUCCESS or not podcast_task.script:
                    raise ValueError("Script must be successfully generated before audio can be created")

                if USE_CELERY:
                    # Enqueue Celery task
                    generate_audio_task.apply_async(args=[self.task_id])
                else:
                    # Enqueue non-blocking async task
                    self._enqueue_generate_audio_task()

                session.commit()  # Ensure any changes are persisted
            return {
                "task_id": self.task_id, "status": TaskStatus.PENDING
            }
        except Exception as e:
            logger.error(f"Failed to enqueue audio task: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to enqueue audio task: {e}")

    def _execute_create_podcast_task(self, podcast_request):
        try:
            self._update_task_status(self.task_id, TaskStatus.STARTED)

            # Create the Podcast object
            my_podcast = FiCastPodcast(
                topic=podcast_request.topic,  # Accessing attributes using dot notation
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
            my_podcast.create()
            script = my_podcast.json_script
            chat_history = my_podcast.raw_script

            # Update the task in the database
            podcast_task = self.db.query(PodcastTask).filter(PodcastTask.task_id == self.task_id).first()
            if not podcast_task:
                raise ValueError("Podcast task not found")
            podcast_task.script = script
            podcast_task.script_status = TaskStatus.SUCCESS
            podcast_task.chat_history = chat_history
            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to create podcast: {e}")
            self.db.rollback()
            self._update_task_status(self.task_id, TaskStatus.FAILURE)
        finally:
            # Ensure thread cleanup
            if self.thread:
                self.thread.join()
                self.thread = None


    def _enqueue_generate_audio_task(self):
        # Simulate non-blocking task execution
        task_thread = threading.Thread(
            target=self._execute_generate_audio_task)
        task_thread.start()

    def _execute_generate_audio_task(self):
        logger.info(f"Executing audio generation for task ID: {self.task_id}")

        try:
            # Re-fetch the podcast task using a fresh session to avoid detached objects
            with SessionLocal() as session:
                podcast_task = session.query(PodcastTask).filter(PodcastTask.task_id == self.task_id).first()

                if not podcast_task:
                    logger.error(f"Podcast task {self.task_id} not found during audio generation.")
                    raise ValueError("Podcast task not found")

                self._update_task_status(session, TaskStatus.STARTED, is_audio=True)

                # Reconstruct the podcast object from the chat history
                logger.info(f"Reconstructing podcast object for task ID: {self.task_id}")
                my_podcast = FiCastPodcast.from_chat_history(podcast_task.chat_history)

                # Synthesize dialogue to create audio
                dialoguer = DialogueSynthesis(
                    client_type="api",
                    base_url=os.getenv("TTS_API_BASE_URL"),
                    api_key=os.getenv("TTS_API_KEY")
                )

                ficast = FiCast(
                    conversation=my_podcast, dialogue_synthesizer=dialoguer)
                my_audio = ficast.to_podcast(ignore_errors=True)
                # Update the task with the new audio and mark audio task as SUCCESS
                podcast_task.audio = my_audio
                podcast_task.audio_status = TaskStatus.SUCCESS
                session.commit()

                logger.info(f"Audio generation completed for task ID: {self.task_id}")

        except Exception as e:
            logger.error(f"Failed to generate audio for task ID: {self.task_id}: {e}")
            with SessionLocal() as session:
                self._update_task_status(
                    session, TaskStatus.FAILURE, is_audio=True)
            raise

    def _update_task_status(
        self, session: Session, status: TaskStatus, is_audio: bool = False
        ):
        try:
            task: PodcastTask = session.query(PodcastTask).filter(PodcastTask.task_id == self.task_id).first()
            if not task:
                logger.error(f"Task {self.task_id} not found when trying to update status.")
                raise ValueError("Task not found")

            if is_audio:
                task.audio_status = status
            else:
                task.script_status = status

            session.commit()
            logger.info(f"Task ID {self.task_id} status updated to {status}")

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update task status for task ID {self.task_id}: {e}")
            raise
        

@shared_task(bind=True)
def create_podcast_task(self, task_id, podcast_request):
    task = Task(db=get_db())
    task._execute_create_podcast_task(podcast_request)

@shared_task(bind=True)
def generate_audio_task(self, task_id):
    task = Task(db=get_db())
    task._execute_generate_audio_task()