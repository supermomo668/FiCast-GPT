from thought_agents.ontology.chats.client import AutogenLLMConfig
from hydra import initialize, compose
from typing import Any

from ficast.assembly.base import ConvCast
from ficast.dialogue.synthesis import DialogueSynthesis 
from ficast.conversation.podcast import Podcast

class Ficast(ConvCast):
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
    conversation: Podcast
    dialogue: DialogueSynthesis = DialogueSynthesis

    def __init__(
        self, 
        conversation: Podcast,
        ):
        self.conversation = conversation

    def inject_music(self, style: str = "auto") -> None:
        """Inject music into the podcast."""
        # TODO: Implement music injection based on style
        print(f"Injecting {style} music into the podcast.")

    def to_podcast(self) -> str:
        """Convert the conversation to an audio podcast."""
        # TODO: Implement conversion to audio podcast
        print("Converting conversation to audio podcast.")
        return "Audio podcast content"
