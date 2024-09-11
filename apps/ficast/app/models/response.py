from os import error
from pydantic import BaseModel
from typing import Optional
from .task_status import TaskStatus

class TaskStatusResponse(BaseModel):
    script_status: TaskStatus
    audio_status: TaskStatus
    error: Optional[str] = None