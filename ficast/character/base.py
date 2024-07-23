import re
from typing import Optional, List
from pydantic import BaseModel

from thought_agents.ontology.config.dialogue import Person, AutogenLLMConfig, ConversationConfig

from .config import default_cfg   # same as podcast config

def match_string_against_list(s: str, allowed_list: List[str]) -> bool:
    """
    Match a string against a list of allowed items using regex.

    Args:
        s (str): The string to be matched.
        allowed_list (List[str]): The list of allowed items.

    Returns:
        bool: True if the string matches any item in the allowed list, False otherwise.
    """
    for pattern in allowed_list:
        # Special case: if the pattern is "*", match any string
        if pattern == "*":
            return True
        # Compile the pattern into a regex
        regex = re.compile(pattern)
        # Check if the string matches the pattern
        if regex.fullmatch(s):
            return True
    return False

class Character(Person):
    """
    A class to represent a podcast participant.

    Attributes:
    -----------
    name : str
        Name of the podcaster.
    desc : str
        Description of the podcaster.
    mode : str
        Mode of participation (e.g., 'podcast').

    Methods:
    --------
    introduce():
        Returns an introduction string for the podcaster.
    """
    cfg: ConversationConfig = default_cfg
    system_message: str = "As yourself: {name}, respond to the conversation."
    name: str
    role: str
    description: str
    model: str
    class Config:
        arbitrary_types_allowed = True
    def __init__(
        self, 
        name: str,
        role: str = "participant",
        description: str = "",
        system_message: str = "As yourself: {name}, respond to the conversation.",
        model: str = "gemini-1.5-pro",
        ):
        super().__init__(name=name, description=description, role=role, model=model)
        self.cfg.llm_config = AutogenLLMConfig(**{"filter_dict": {"model": [model]}})
        self.system_message = system_message.format_map({"name": name})
        assert match_string_against_list(role, self.__allowed_roles__()), "Invalid role, must be one of {}".format(self.__allowed_roles__)
        
    def _inject_description(self):
        raise NotImplementedError("Please implement _inject_description()")
        
    def introduce(self) -> str:
        """Return an introduction string for the podcaster."""
        return f"{self.name}: {self.desc}"
    
    @property
    def __allowed_roles__(self):
        return ["*"]
# default character

