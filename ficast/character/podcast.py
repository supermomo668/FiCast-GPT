import warnings
import autogen 

import gender_guesser.detector as gd

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
    def __init__(
      self, 
      name: str,
      description: str,
      model: str = "gemini-1.5-pro",
      role: str = "guest",
      gender: str = None,
      system_message: str = "As yourself: {name}, respond to the conversation.",
      ):
      super().__init__(
        name=name, 
        description=description, 
        system_message=system_message, 
        model=model, 
        role=role,
        gender=gender
      )
      self.system_message = self.cfg.system_prompts['podcast'][role].format_map({
        "name": name, "parser": dialogue_parser.get_format_instructions()
      })
      gender_detector = gd.Detector()
      if self.gender is None:
        self.gender = gender_detector.get_gender(name.split()[0])
        warnings.warn(f"Gender not specified for {name}, assigned gender for {name} as {self.gender}")
      
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