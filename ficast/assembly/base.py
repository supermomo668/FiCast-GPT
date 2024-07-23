import os
from typing import Any

from ficast.character.podcast import Podcaster
from ficast.conversation.base import Conversation

from elevenlabs.client import ElevenLabs

client = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY")
)

class ConvCast:
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

    def __init__(self, config: Any, conversation: Conversation):
        self.config = config
        self.conversation = conversation

    def text_to_speech(self, text: str) -> str:
        """Convert the conversation to an audio podcast."""
        # TODO: Implement conversion to audio podcast
        print("Converting conversation to audio podcast.")
        return "Audio podcast content"
