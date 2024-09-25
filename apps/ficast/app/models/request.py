from typing import Optional
from pydantic import BaseModel

class Participant(BaseModel):
    name: str
    description: Optional[str] = None
    model: Optional[str] = None
    role: Optional[str] = "guest"

class PodcastRequest(BaseModel):
    topic: str
    n_rounds: int
    participants: list[Participant]

class TaskRequest(BaseModel):
    task_id: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
