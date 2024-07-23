from abc import ABC, abstractmethod
from typing import List

import autogen

from thought_agents.ontology.config.dialogue import ConversationConfig, PodcastConfig, PodcastCharacters, Person, AutogenLLMConfig
 

from beartype import beartype

from ficast.character.base import Character

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
  class Config:
      arbitrary_types_allowed = True

  def __init__(
    self, 
    topic: str, 
    participants: List[Character] = [], 
    n_rounds: int = None, 
    output_format: str="json"
    ):
    if n_rounds is None:
      n_rounds = len(participants)+1
    self.topic = topic
    self._init_agents()

  def _init_agents(self):
    self.initializer = autogen.UserProxyAgent(
        name="init", 
        code_execution_config=False,
        system_message=f"Have a conversation on the topic: {self.topic} among the characters: {self.participants} as in a real-life conversation. The dialogue are eventually compiled into a JSON transcript.",   
    )
    self.all_agents = [self.initializer] + self.participant_agents

  def add(self, participants):
    """Add participants to the conversation."""
    if type(participants) is list:
        self.participants.extend(participants)
    if issubclass(Character, participants.__class__):
        self.participants.append(participants)
      
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
    
  def create(self):
    if not hasattr(self, 'groupchat_manager'):
      self._create_conv_group()
    return self.initializer.initiate_chat(
      self.groupchat_manager, 
      message=self.cfg.system_prompts[self.conv_mode]["initiation"].format(
      characters=",".join([p.name for p in self.participants]),
      topic=self.cfg.podcast_config.topic
      )
    )