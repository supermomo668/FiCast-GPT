from logging import warning
from typing import Dict, List
import warnings
from beartype import beartype
import re, json
from datetime import datetime
from pathlib import Path
import autogen

from thought_agents.ontology.config.dialogue import ConversationConfig
from thought_agents.ontology.parser.dialogue import Podcast
 
from .base import Conversation
from ficast.character.podcast import Character, Podcaster
from ficast.config import load_podcast_config
from thought_agents.dialogue.agents import agent_registry

from thought_agents.dialogue.transition import get_state_transition
from .utils import extract_json_code_block, save_json_based_script, save_raw_based_script


class Podcast(Conversation):
  n_rounds: int
  topic: str
  output_format: str = "json"
  participants: List[Podcaster] = []
  cfg: ConversationConfig = load_podcast_config()
  conv_mode: str = "podcast"
  class Config:
    arbitrary_types_allowed = True

  def __init__(
    self,
    topic: str, 
    participants: List[Character] = [], 
    n_rounds: int =None, 
    ):
    
    super().__init__(
      topic=topic, participants=participants, n_rounds=n_rounds, output_format=self.output_format
    )
    # self.cfg = load_podcast_config()  # Assuming conv_cfg is defined elsewhere
    self.initializer = autogen.UserProxyAgent(
      name="init", 
      code_execution_config=False,
    )
    self.cfg.podcast_config.n_rounds = n_rounds
    self.cfg.podcast_config.topic = topic
    
  @property
  def agent_chain(self) -> List[autogen.Agent]:
    # create research_agents: research_coder, executor, informer
    research_agents = agent_registry.get_class("dialogue.research")(
      self.cfg.llm_config, self.cfg.system_prompts)
    script_parser = agent_registry.get_class("podcast.parser")(
      self.cfg.llm_config, self.cfg.system_prompts)
    # create podcast agents:  podcast_host, podcast_guests
    agents = [self.initializer]
    for a in [
      research_agents, self.host_agents, self.guest_agents, script_parser]:
      agents.extend(a)
    return agents
  
  @property
  def hosts(self) -> List[Podcaster]:
    return [p for p in self.participants if p.role=="host"]
  @property
  def host_agents(self) -> List[Podcaster]:
    return [p.agent for p in self.participants if p.role=="host"]
  @property
  def guests(self) -> List[Podcaster]:
    return [p for p in self.participants if p.role=="guest"]
  @property
  def guest_agents(self) -> List[Podcaster]:
    return [p.agent for p in self.participants if p.role=="guest"]
  
  def _validate_participants(self):
    # min 2 participants
    if self.n_participants < 2:
      raise ValueError(f"Podcast requires at least 2 participants. currently: {self.n_participants}")
    # require host
    if not any([p.role=="host" for p in self.participants]):
      raise ValueError("Podcast requires at least 1 host.")
    # require guest
    if not any([p.role=="guest" for p in self.participants]):
      raise ValueError("Podcast requires at least 1 guest.")
  
  def _set_character_cfg(self):
    self.cfg.podcast_config.character_cfg.hosts = self.hosts
    self.cfg.podcast_config.character_cfg.guests = self.guests
    
  def _create_conv_group(self):
    self._validate_participants()
    self._set_character_cfg()
    podcast_cfg = self.cfg.podcast_config
    groupchat = autogen.GroupChat(
        agents=self.agent_chain,
        messages=[],
        max_round=podcast_cfg.n_rounds,
        speaker_selection_method=get_state_transition(
          podcast_cfg, 
          transition=f"podcast.default", 
          MAX_ROUND=podcast_cfg.n_rounds
        ),
    )
    self.groupchat_manager = autogen.GroupChatManager(
        groupchat=groupchat, 
        llm_config=self.cfg.llm_config.model_dump()
    )
  
  def get_script(
    self, mode='json', create_if_not:bool = True
    ):
    if not hasattr(self, 'chat_history'):
      if create_if_not:
        self.create()
      else:
        raise ValueError("Podcast conversation has not been created yet. Use `.create()` to create the conversation.")
    match mode:
      case 'json':
        self.script = self.json_script
      case 'raw': 
        self.script = self.raw_script
      case 'raw-json':
        self.script = []
        for c in self.raw_script:
          try:
            self.script.append(extract_json_code_block(c['content']))
          except Exception as e:
            warnings.warn(f"Error parsing script: {e}, returning correct but likely incomplete script.")
      case _:
        raise ValueError(f"Invalid mode: {mode}. Valid modes are: json, raw, raw-json.")
    return self.script
  
  @property
  def raw_script(self, create_if_na:bool = True) -> Dict[str, str]:
    # return only the chat history concerning podcast agents
    n_research_agents = len(agent_registry.get_class("dialogue.research")(
      self.cfg.llm_config, self.cfg.system_prompts))
    return self.chat_history[n_research_agents:-1]
    
  @property
  def json_script(self) -> Dict | Podcast:
    if 'content' in self.chat_history[-1]:
        return extract_json_code_block(self.chat_history[-1]['content'])
    else:
      raise ValueError("key `content` not found in  `chat_history` object.")

  def save_script(self, save_path: str = None, option: str = "json") -> None:
    if not hasattr(self, 'chat_history'):
      raise ValueError("Podcast conversation has not been created yet. Use `.create()` to create the conversation.")
    options={"json", "human", "text", "html"}
    if not save_path:
      output_dir = Path("ficast-outputs/scripts")
      output_dir.mkdir(parents=True, exist_ok=True)
      path = output_dir / f"script_{self.created_at}_{option}.txt"
    else:
      path = Path(save_path)
    # Call the appropriate function based on the option
    if option.lower() in ["json", "human"]:
      save_json_based_script(self.json_script, path, option)
    elif option.lower() in ["text", "html"]:
      save_raw_based_script(self.raw_script, path, option)
    else:
      raise ValueError(f"Unsupported option '{option}' provided. Supported options are 'json', 'text', 'html', and 'human'.")
    print(f"Script saved to {path}")
    
  @classmethod
  @beartype
  def from_chat_history(cls, chat_history: List[Dict]):
    """
    Class method to create a Podcast instance from a given chat history.
    """
    # Initialize an instance with default or dummy arguments
    instance = cls(
      topic="", participants=[], n_rounds=0)
    # Set the chat history
    instance.chat_history = chat_history
    return instance