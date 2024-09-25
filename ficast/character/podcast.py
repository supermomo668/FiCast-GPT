from typing import Optional
import warnings
import autogen 

from pydantic import Field, field_validator
from thought_agents.dialogue.utils import termination_msg
from thought_agents.ontology.parser.dialogue import dialogue_parser

from .base import Character

class Podcaster(Character):
    """
    A class to represent a specific type of Character, which is a Podcaster.

    Attributes:
    -----------
    name : str
        Name of the podcaster.
    description : str
        Description of the podcaster.
    mode : str
        Mode of participation (e.g., 'podcast').

    Methods:
    --------
    introduce():
        Returns an introduction string for the podcaster.
    """
    model: Optional[str] = Field(default="gemini-1.5-pro")
    @field_validator('model')
    def set_default_model(cls, v):
        if v is None:
            return "gemini-1.5-pro"
        return v

    def __init__(
      self, 
      name: str,
      description: Optional[str] = None,
      model: Optional[str] = Field(default="gemini-1.5-pro"),
      role: str = "guest",
      sex: Optional[str] = None,
      system_message: str = "As yourself: {name}, respond to the conversation.",
      ):
      """
      Initialize a Podcaster instance.
      Parameters:
      -----------
      name : str
          Name of the podcaster.
      description : str, optional
          Description of the podcaster. Defaults to None.
      model : str, optional
          Model name for the podcaster. Defaults to "gemini-1.5-pro".
      role : str, optional
          Role of the podcaster. Defaults to "guest".
      gender : str, optional
          Gender of the podcaster. Defaults to None.
      system_message : str, optional
          System message for the podcaster. Defaults to
          "As yourself: {name}, respond to the conversation.".
      """
      super().__init__(
        name=name, 
        description=description, 
        system_message=system_message, 
        model=model, 
        role=role,
        sex=sex
      )
      self.system_message = self.cfg.system_prompts['podcast'][role].format_map({
        "name": name, "parser": dialogue_parser.get_format_instructions()
      })
      
    def __allowed_roles__(self):
      return ["host", "guest"]
    
    @property
    def agent(self):
      return autogen.ConversableAgent(
        name=self.name,  
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config=self.cfg.llm_config.model_dump(),
        description=self.description,
        system_message=self.system_message
      )