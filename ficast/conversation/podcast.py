from logging import warning
from typing import Dict, List
import warnings
from beartype import beartype
import re, json
from datetime import datetime
from pathlib import Path
import autogen

from thought_agents.ontology.config.dialogue import ConversationConfig, PodcastConfig
 
from .base import Conversation
from ficast.character.podcast import Character, Podcaster

from thought_agents.dialogue.agents import agent_registry

from thought_agents.dialogue.transition import get_state_transition
from .config import conv_cfg
from .utils import extract_json_code_block, save_json_based_script, save_raw_based_script


class Podcast(Conversation):
  n_rounds: int
  topic: str
  output_format: str = "json"
  participants: List[Podcaster] = []
  cfg: ConversationConfig = conv_cfg
  podcast_cfg: PodcastConfig = conv_cfg.podcast_config
  conv_mode: str = "podcast"
  class Config:
    arbitrary_types_allowed = True

  def __init__(
    self,
    topic: str, 
    participants: List[Character] = [], 
    n_rounds: int =None, 
    ):
    
    super().__init__(topic=topic, participants=participants, n_rounds=n_rounds, output_format=self.output_format)
    # self.config = conv_cfg  # Assuming conv_cfg is defined elsewhere
    self.initializer = autogen.UserProxyAgent(
      name="init", 
      code_execution_config=False,
    )
    self.podcast_cfg.n_rounds = n_rounds
    self.podcast_cfg.topic = topic
    
  @property
  def agent_chain(self) -> List[autogen.Agent]:
    # create research_agents: research_coder, executor, informer
    research_agents = agent_registry.get_class("dialogue.research")(
      self.cfg.llm_config, self.cfg.system_prompts)
    script_parser = agent_registry.get_class("podcast.parser")(
      self.cfg.llm_config, self.cfg.system_prompts)
    # create podcast agents:  podcast_host, podcast_guests
    agents = [self.initializer]
    for a in [research_agents, self.host_agents, self.guest_agents, script_parser]:
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
    self.podcast_cfg.character_cfg.hosts = self.hosts
    self.podcast_cfg.character_cfg.guests = self.guests
    
  def _create_conv_group(self):
    self._validate_participants()
    self._set_character_cfg()
    groupchat = autogen.GroupChat(
        agents=self.agent_chain,
        messages=[],
        max_round=self.podcast_cfg.n_rounds,
        speaker_selection_method=get_state_transition(
          self.podcast_cfg, 
          transition=f"podcast.default", 
          MAX_ROUND=self.podcast_cfg.n_rounds
        ),
    )
    self.groupchat_manager = autogen.GroupChatManager(
        groupchat=groupchat, 
        llm_config=self.cfg.llm_config.model_dump()
    )
  
  @property
  def raw_script(self) -> Dict[str, str]:
    # return only the chat history concerning podcast agents
    return self.chat_history[4:-1]
    
  @property
  def script(self) -> Dict:
    # return only the chat history concerning podcast agents
    json_script = []
    for c in self.raw_script:
      try:
        json_script.append(extract_json_code_block(c['content']))
      except Exception as e:
        warnings.warn(f"Error parsing script: {e}, returning correct but likely incomplete script.")
        return json_script
    return json_script
   
  @property
  def json_script(self) -> Dict:
    if hasattr(self, 'chat_history'):
      # return the script in json dictionary from `script_parser` agent
      if 'content' in self.chat_history[-1]:
        return extract_json_code_block(self.chat_history[-1]['content'])
      else:
        raise ValueError("Podcast conversation is not created correctly. Fix the script generation in `.create()`. The final user should be a script parser agent. Or access the `script` attribute referencecd from chat_history directly.")
    else:
      raise ValueError("Podcast conversation has not been created yet. Use `.create()` to create the conversation.")

  def save_script(self, path: str = None, option: str = "json") -> None:
    if not hasattr(self, 'chat_history'):
      raise ValueError("Podcast conversation has not been created yet. Use `.create()` to create the conversation.")
    options={"json", "human", "text", "html"}
    if path is None:
      output_dir = Path("ficast-outputs/scripts")
      output_dir.mkdir(parents=True, exist_ok=True)
      path = output_dir / f"script_{self.created_at}_{option}.txt"
    else:
      path = Path(path)
    # Call the appropriate function based on the option
    if option.lower() in ["json", "human"]:
      save_json_based_script(self.json_script, path, option)
    elif option.lower() in ["text", "html"]:
      save_raw_based_script(self.raw_script, path, option)
    else:
      raise ValueError(f"Unsupported option '{option}' provided. Supported options are 'json', 'text', 'html', and 'human'.")
    print(f"Script saved to {path}")