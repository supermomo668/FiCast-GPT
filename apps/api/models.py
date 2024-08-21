from pydantic import BaseModel

class PodcastRequest(BaseModel):
    topic: str
    n_rounds: int
    participants: list[str]

class Token(BaseModel):
    access_token: str
    token_type: str
