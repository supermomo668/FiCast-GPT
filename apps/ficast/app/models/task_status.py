from enum import Enum
from typing import Optional

from pydantic import BaseModel

class TaskStatus(str, Enum):
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

# Response & Request

class TaskType(str, Enum):
    SCRIPT = "script"
    AUDIO = "audio"
    
class TaskProgressRequest(BaseModel):
    task_id: str
    event_type: Optional[TaskType] = None
    
class TaskStatusResponse(BaseModel):
    status : Optional[TaskStatus] = None
    script_status: Optional[TaskStatus] = None
    audio_status: Optional[TaskStatus] = None
    error: Optional[str] = None