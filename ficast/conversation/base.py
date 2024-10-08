from abc import ABC, abstractmethod
from typing import List, TypeVar
import warnings
from datetime import datetime

import autogen

from thought_agents.ontology.config.dialogue import ConversationConfig, PodcastConfig, PodcastCharacters, Person, AutogenLLMConfig
 

from beartype import beartype

from ficast.character.base import Character

CH = TypeVar('CH', bound=Character)

class Conversation:
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

  n_rounds: int
  topic: str
  output_format: str
  participants: List[Character] = []
  conv_mode: str = "podcast"
  created_at: datetime 

  class Config:
      arbitrary_types_allowed = True

  def __init__(
    self, 
    topic: str, 
    n_rounds: int, 
    participants: List[Character] = [], 
    output_format: str="json"
    ):
    self.participants = participants
    self.topic = topic
    self._init_agents()

  def _init_agents(self):
    self.initializer = autogen.UserProxyAgent(
        name="init", 
        code_execution_config=False,
        system_message=f"Have a conversation on the topic: {self.topic} among the characters: {self.participants} as in a real-life conversation. The dialogue are eventually compiled into a JSON transcript.",   
    )
    self.all_agents = [self.initializer] + self.participant_agents

  def _validate_new_participants(
    self, participants: List[Character]):
    for p in participants:
      if p in self.participants:
        warnings.warn(f"Participant `{p.name}` is already in the conversation. Skipping")
        
  @beartype  
  def add(self, participants: List[CH] | CH):
    """Add participants to the conversation."""
    self._validate_new_participants(participants)
    if issubclass(Character, participants.__class__):
      participants = [participants]
    for p in participants:
      if p not in self.participants:
        if p.name not in [p.name for p in self.participants]:
          self.participants.append(p)
        else:
          warnings.warn("Participant name already in conversation. To add a participant, use a unique name. Skipping.")
      
  @property
  def n_participants(self) -> int:
    return len(self.participants)
  
  @property
  def participant_agents(self) -> List[autogen.ConversableAgent]:
    
    """
    Returns a list of `autogen.ConversableAgent` objects, where each object is
    created by calling the `_participant_to_character` method on each participant
    in the `self.participants` list.

    :return: A list of `autogen.ConversableAgent` objects.
    :rtype: List[autogen.ConversableAgent]
    """
    return [p.agent for p in self.participants]
  
  @abstractmethod
  def agent_chain(self) -> List[autogen.Agent]:
    """
    Returns a list of `autogen.Agent` objects, where the first element is the `initializer` and the remaining elements are the `characters`.

    :return: A list of `autogen.Agent` objects.
    :rtype: List[autogen.Agent]
    """
    return []
  
  @abstractmethod
  def create_conv_group(self, cfg: ConversationConfig):
    """
    Create a conversation group.

    Args:
        cfg (ConversationConfig): The configuration for the conversation.

    Returns:
        Tuple[autogen.Agent, autogen.GroupChatManager]: A tuple containing the initializer agent and the group chat manager.
    """
    # create podcast agents:  podcast_host, podcast_guests
    groupchat = autogen.GroupChat(
      agents=self.agent_chain,
      messages=[],
      max_round=self.n_rounds,
      speaker_selection_method="auto"
    )
    return self.initializer, autogen.GroupChatManager(
        groupchat=groupchat, 
        llm_config=cfg.llm_config.model_dump()
    )
    
  def create(self) -> autogen.agentchat.chat.ChatResult:
    if not hasattr(self, 'groupchat_manager'):
      # create groupchat manager if not exist 
      self._create_conv_group()
    self.chat_history =  self.initializer.initiate_chat(
      self.groupchat_manager, 
      message=self.cfg.system_prompts[self.conv_mode]["initiation"].format(
      characters=",".join([
        p.name for p in self.participants
      ]),
      topic=self.cfg.podcast_config.topic,
      length=self.cfg.podcast_config.length
      )
    ).chat_history   # chatResult := id, chat_history
    self.created_at = datetime.now().strftime("%Y%m%d_%H%M%S")
    return self.chat_history
    
  
  