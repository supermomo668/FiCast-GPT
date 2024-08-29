from typing import Optional
from pydantic import BaseModel

class Participant(BaseModel):
    name: str
    description: str
    model: str
    role: Optional[str] = None

class PodcastRequest(BaseModel):
    topic: str
    n_rounds: int
    participants: list[Participant]

class Token(BaseModel):
    access_token: str
    token_type: str
