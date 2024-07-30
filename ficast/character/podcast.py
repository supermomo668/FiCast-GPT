import autogen 

from thought_agents.dialogue.utils import termination_msg
from thought_agents.ontology.parser.dialogue import monologue_parser

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
      role: str = "guest",
      description: str = "",
      system_message: str = "As yourself: {name}, respond to the conversation.",
      model: str = "gemini-1.5-pro"
      ):
      super().__init__(
        name=name, 
        description=description, 
        system_message=system_message, 
        model=model, 
        role=role
      )
      self.system_message = self.cfg.system_prompts['podcast'][role].format_map({
        "name": name, "parser": monologue_parser.get_format_instructions()
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


