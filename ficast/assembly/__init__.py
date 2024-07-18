from ficast.character.podcaster import Podcaster
from ficast.conversation.podcast import create_podcast_group, ConversationConfig
from pydantic import BaseModel
from typing import List, Dict, AnyStr

class Conversation(BaseModel):
    type: str
    n_rounds: int
    topic: str
    output_format: str
    participants: List[str] = []

    def add(self, participant_names: List[str]):
      self.participants.extend(participant_names)

class FiCast:
    def __init__(self, conf: ConversationConfig, conversation: Conversation):
        self.conf = conf
        self.conversation = conversation

    def inject_music(self, style: str = "auto"):
        # Placeholder for music injection logic
        # TODO: Add actual music injection implementation
        print(f"Injecting {style} music into the podcast.")
        return self

    def to_podcast(self):
        # Placeholder for converting conversation to podcast logic
        # TODO: Add actual conversation to podcast conversion implementation
        print("Converting conversation to podcast format.")
        return self
