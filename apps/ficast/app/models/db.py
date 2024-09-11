import json
from sqlalchemy import JSON, Column, Integer, String, Text, LargeBinary, Enum
from .task_status import TaskStatus
from .base import Base
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

    task_id = Column(String, unique=True, primary_key=True, index=True)
    script_status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)  # Status for script generation
    script = Column(JSON, nullable=True)  # Stores the JSON script (nullable initially)
    chat_history = Column(JSONEncodedDict, nullable=False)  # Stores the chat history (nullable initially)
    audio_status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)  # Status for audio generation
    audio = Column(LargeBinary, nullable=True)  # Stores the audio file as binary data
    error_message = Column(Text, nullable=True)  # New field to store errors

    def __init__(self, task_id: str, script_status: TaskStatus = TaskStatus.PENDING, audio_status: TaskStatus = TaskStatus.PENDING, error_message: str = None):
        
        self.task_id = task_id
        self.script_status = script_status
        self.audio_status = audio_status
        self.error_message = error_message
