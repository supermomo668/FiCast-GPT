import uuid
import os
from sqlalchemy.orm import Session
from ficast.conversation.podcast import Podcast as FiCastPodcast
from ficast.character.podcast import Podcaster
from ficast.assembly.ficast import FiCast
from ficast.dialogue.speech import DialogueSynthesis

from .logger import logger
from .models.db import PodcastTask
from .models.task_status import TaskStatus

class Task:
    def __init__(self, db: Session):
        self.db = db
        self.task_id = str(uuid.uuid4())
        logger.info(f"Assigned Task ID: {self.task_id}")

    def create_podcast(self, podcast_request):
        try:
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
            my_podcast.create()
            script = my_podcast.json_script
            chat_history = my_podcast.raw_script

            # Save to database with script status SUCCESS
            new_task = PodcastTask(
                task_id=self.task_id,
                script_status=TaskStatus.SUCCESS,
                script=script,
                chat_history=chat_history
            )
            self.db.add(new_task)
            self.db.commit()

            return self.task_id

        except Exception as e:
            logger.error(f"Failed to create podcast: {e}")
            self.db.rollback()
            raise

    def generate_audio(self):
        try:
            podcast_task = self.db.query(PodcastTask).filter(PodcastTask.task_id == self.task_id).first()
            if not podcast_task:
                raise ValueError("Podcast task not found")

            if podcast_task.script_status != TaskStatus.SUCCESS or not podcast_task.script:
                raise ValueError("Script must be successfully generated before audio can be created")

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

            # Update the task with the new audio and mark audio task as SUCCESS
            podcast_task.audio = my_audio
            podcast_task.audio_status = TaskStatus.SUCCESS
            podcast_task.chat_history = my_podcast.raw_script  # Update chat history with any new content

            self.db.commit()

            return self.task_id

        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            self.db.rollback()
            raise

    def update_task_status(self, task_id: str, status: TaskStatus, is_audio: bool = False):
        try:
            task = self.db.query(PodcastTask).filter(PodcastTask.task_id == task_id).first()
            if not task:
                raise ValueError("Task not found")

            if is_audio:
                task.audio_status = status
            else:
                task.script_status = status

            self.db.commit()

        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            self.db.rollback()
            raise
