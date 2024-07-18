from pydantic import BaseModel
from typing import List

from beartype import beartype

from ficast.character.base import Character

class Conversation(BaseModel):
    """
    A class to represent a podcast conversation.

    Attributes:
    -----------
    type : str
        Type of conversation (e.g., 'podcast').
    n_rounds : int
        Number of rounds in the conversation.
    topic : str
        Topic of the conversation.
    output_format : str
        Format of the output (e.g., 'json').

    Methods:
    --------
    add(participants: List[str]):
        Adds participants to the conversation.
    """

    type: str
    n_rounds: int
    topic: str
    output_format: str
    participants: List[Character] = []
    
    @beartype
    def add(self, participants: List[str]):
        """Add participants to the conversation."""
        self.participants.extend(participants)
