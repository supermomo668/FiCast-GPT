from enum import Enum

from pydantic import BaseModel

class TaskStatus(Enum):
    PENDING = "pending"
    STARTED = "started"
    GENERATING_SCRIPT = "generating_script"
    SCRIPT_CREATED = "script_created"
    GENERATING_AUDIO = "generating_audio"
    SUCCESS = "success"
    FAILURE = "failure"
    AUDIO_CREATED = "audio_created"

    @classmethod
    def from_celery_state(cls, state: str):
        """
        Convert a Celery task state to a TaskStatus enum.
        
        :param state: The state string from Celery (e.g., "PENDING", "SUCCESS").
        :type state: str
        :return: Corresponding TaskStatus enum.
        :rtype: TaskStatus
        """
        try:
            return cls[state]
        except KeyError:
            raise ValueError(f"Unknown Celery task state: {state}")

class TaskStatusUpdate(BaseModel):
    task_id: str
    status: TaskStatus