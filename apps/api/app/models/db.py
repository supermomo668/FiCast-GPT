from sqlalchemy import Column, String, Text, LargeBinary, Enum
from .base import Base
from .task_status import TaskStatus

class PodcastTask(Base):
    __tablename__ = 'podcast_tasks'

    task_id = Column(String, primary_key=True, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    script = Column(Text, nullable=False)  # Stores the JSON script (not nullable)
    chat_history = Column(Text, nullable=False)  # Stores the chat history (not nullable)
    audio = Column(LargeBinary, nullable=True)  # Stores the audio file as binary data
    is_audio_task = Column(Enum(TaskStatus), default=TaskStatus.PENDING)  # Track the audio generation status separately

    def __init__(self, task_id: str, script: dict, chat_history: str, script_status: TaskStatus = TaskStatus.PENDING, audio_status: TaskStatus = TaskStatus.PENDING, audio: bytes = None):
        self.task_id = task_id
        self.script = script
        self.chat_history = chat_history
        self.status = script_status
        self.is_audio_task = audio_status
        self.audio = audio
