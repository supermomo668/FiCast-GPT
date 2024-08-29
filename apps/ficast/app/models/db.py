import json
from sqlalchemy import JSON, Column, String, Text, LargeBinary, Enum
from sqlalchemy.ext.declarative import declarative_base
from .task_status import TaskStatus

Base = declarative_base()

from sqlalchemy.types import TypeDecorator

class JSONEncodedDict(TypeDecorator):
    """Enables JSON storage by encoding and decoding JSON objects transparently"""
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)
    
class PodcastTask(Base):
    __tablename__ = 'podcast_tasks'

    task_id = Column(String, primary_key=True, index=True)
    script_status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)  # Status for script generation
    script = Column(JSON, nullable=False)  # Stores the JSON script (nullable initially)
    chat_history = Column(JSONEncodedDict, nullable=False)  # Stores the chat history (nullable initially)
    audio_status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)  # Status for audio generation
    audio = Column(LargeBinary, nullable=True)  # Stores the audio file as binary data

    def __init__(self, task_id: str, script_status: TaskStatus = TaskStatus.PENDING, script: dict = None, chat_history: str = None, audio_status: TaskStatus = TaskStatus.PENDING, audio: bytes = None):
        self.task_id = task_id
        self.script_status = script_status
        self.script = script
        self.chat_history = chat_history
        self.audio_status = audio_status
        self.audio = audio
