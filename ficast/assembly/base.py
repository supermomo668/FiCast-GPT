from abc import abstractmethod
import os
from typing import Any
from pydantic import BaseModel

from ficast.conversation.base import Conversation

from elevenlabs.client import ElevenLabs

client = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY")
)

class ConvCast(BaseModel):
    """
    A class to assemble and create a podcast conversation.

    Attributes:
    -----------
    config : Any
        Configuration for the podcast.
    conversation : Conversation
        Conversation object with details of the podcast.

    Methods:
    --------
    inject_music(style: str) -> 'FiCast':
        Injects music into the podcast.
    to_podcast() -> str:
        Converts the conversation to an audio podcast.
    """
    conversation: Conversation
    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True,  # Updated for Pydantic V2
        "protected_namespaces": (),  # Avoid conflict with 'model_'
    }
    
    def __init__(self, conversation: Conversation, **kwargs: Any):
        super().__init__(**kwargs)
        self.conversation = conversation

    @abstractmethod
    def to_podcast(self, text: str) -> str:
        """Convert the conversation script to an audio podcast."""
        # TODO: Implement conversion to audio podcast
        print("Converting conversation to audio podcast.")
        raise NotImplementedError