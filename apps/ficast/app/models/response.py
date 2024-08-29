from pydantic import BaseModel
from .task_status import TaskStatus

class TaskCreate(BaseModel):
    task_id: str
    status: TaskStatus

class TaskStatusResponse(BaseModel):
    script_status: TaskStatus
    audio_status: TaskStatus
    