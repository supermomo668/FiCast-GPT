from sqlalchemy import Column, String, Text, LargeBinary, Enum
from sqlalchemy.ext.declarative import declarative_base
from .task_status import TaskStatus

Base = declarative_base()

class PodcastTask(Base):
    __tablename__ = 'podcast_tasks'

    task_id = Column(String, primary_key=True, index=True)
    script_status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)  # Status for script generation
    script = Column(Text, nullable=True)  # Stores the JSON script (nullable initially)
    chat_history = Column(Text, nullable=True)  # Stores the chat history (nullable initially)
    audio_status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)  # Status for audio generation
    audio = Column(LargeBinary, nullable=True)  # Stores the audio file as binary data

    def __init__(self, task_id: str, script_status: TaskStatus = TaskStatus.PENDING, script: dict = None, chat_history: str = None, audio_status: TaskStatus = TaskStatus.PENDING, audio: bytes = None):
        self.task_id = task_id
        self.script_status = script_status
        self.script = script
        self.chat_history = chat_history
        self.audio_status = audio_status
        self.audio = audio
