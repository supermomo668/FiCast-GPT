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
  participants: List[Podcaster]
  output_format: str = "json"
  cfg: ConversationConfig = load_podcast_config()
  conv_mode: str = "podcast"
  class Config:
    arbitrary_types_allowed = True

  def __init__(
      self,
      topic: str, 
      participants: List[Character] = None,  # Avoid using [] as default
      n_rounds: int = None,
  ):
    if participants is None:
        participants = []  # Initialize an empty list if None is passed
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
  def research_agents(self) -> List[autogen.Agent]:
    return agent_registry.get_class("dialogue.research")(self.cfg.llm_config, self.cfg.system_prompts)
    
  @property
  def agent_chain(self) -> List[autogen.Agent]:
    # create research_agents: research_coder, executor, informer
    script_parser = agent_registry.get_class("podcast.parser")(
      self.cfg.llm_config, self.cfg.system_prompts)
    # create podcast agents:  podcast_host, podcast_guests
    agents = [self.initializer]
    for a in [
      self.research_agents, self.host_agents, self.guest_agents, script_parser]:
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
    """
    Creates a conversation group (GroupChat) and a manager for it based on the current configuration and participant list.

    :return: None
    """
    self._set_character_cfg()
    podcast_cfg = self.cfg.podcast_config
    # compensate number of rounds : research + parsing
    max_podcast_rounds = podcast_cfg.n_rounds + len(self.research_agents) + 1
    groupchat = autogen.GroupChat(
        agents=self.agent_chain,
        messages=[],
        max_round=max_podcast_rounds,
        speaker_selection_method=get_state_transition(
          podcast_cfg, 
          transition=f"podcast.default",
          MAX_ROUND=max_podcast_rounds
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
    n_research_agents = len(self.research_agents)
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
      Reconstructs the Podcast object by reverse engineering the chat history data.
      """
      # Initialize an instance with default or dummy arguments
      instance = cls(topic="", participants=[], n_rounds=len(chat_history))

      # Extract participants from chat history
      participants = _extract_participants_from_chat_history(chat_history)
      instance.participants = participants
      # Set the chat history
      instance.chat_history = chat_history
      return instance

  @classmethod
  @beartype
  def from_script(cls, json_script: Dict):
      """
      Class method to create a Podcast instance from a given script.
      Parses the `json_script` and constructs the Podcast object with participants and other metadata.
      """
      # Extract participants (hosts and guests)
      participants = _extract_participants(json_script.get('participants', {}))
      # Initialize the Podcast instance with extracted information
      instance = cls(
          topic=json_script.get('title', ''),
          participants=participants,
          n_rounds=len(json_script.get('dialogues', []))
      )
      instance.chat_history = [{'content': f"```json\n{json.dumps(json_script)}\n```"}]  # Set the json_script
      return instance


# Helper functions

def _extract_participants(participants_data: Dict) -> List[Podcaster]:
    """
    Helper method to extract participants (hosts and guests) from the given participants data.
    """
    participants = []

    # Adding hosts and guests using Podcaster(**data)
    for host in participants_data.get('hosts', []):
        participants.append(Podcaster(**host, role="host"))

    for guest in participants_data.get('guests', []):
        participants.append(Podcaster(**guest, role="guest"))

    return participants


def _convert_dialogues_to_chat_history(dialogues: List[Dict]) -> List[Dict]:
    """
    Helper method to convert dialogues from the script into chat history format.
    """
    chat_history = []
    for dialogue in dialogues:
        chat_history.append({
            'speaker': dialogue['speaker'],
            'content': dialogue['dialogue'],
            'inner_thought': dialogue.get('inner_thought', '')
        })
    return chat_history


def _extract_participants_from_chat_history(chat_history: List[Dict]) -> List[Podcaster]:
    """
    Helper method to extract participants from chat history.
    This is a more complex task as we have to infer the roles and participant details from the chat history.
    """
    participants = []
    speakers = set(entry['speaker'] for entry in chat_history)

    # Assume we can infer roles from the speaker names or metadata
    for speaker in speakers:
        participants.append(Podcaster(name=speaker, role="guest"))

    return participants