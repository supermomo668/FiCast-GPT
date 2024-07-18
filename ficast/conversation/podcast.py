from hydra.core.config_store import ConfigStore
from dataclasses import dataclass, field
from typing import List, Dict, AnyStr

from pydantic import BaseModel, Field
from thought_agents.ontology.chats.client import AutogenLLMConfig

class Person(BaseModel):
    name: AnyStr = Field(..., description="name of the person")
    description: AnyStr = Field(..., description="1-2 line description of the person if known, otherwise just a generic character.")

class PodcastCharacters(BaseModel):
    hosts: List[Person] = Field(..., description="host of the podcast")
    guests: List[Person] = Field(..., description="list of guests of the podcast")

    @property
    def guest_names(self) -> List[AnyStr]:
        return [guest.name for guest in self.guests]

    @property
    def host_names(self) -> List[AnyStr]:
        return [host.name for host in self.hosts]

class PodcastConfig(BaseModel):
    topic: str = Field(..., description="topic of the podcast")
    n_rounds: int = Field(..., description="number of rounds in the podcast")
    character_cfg: PodcastCharacters

class ConversationConfig(BaseModel):
    llm_config: AutogenLLMConfig
    podcast_config: PodcastConfig
    system_prompts: Dict[str, Dict | AnyStr]

# Register the configuration with ConfigStore
cs = ConfigStore.instance()
cs.store(name="podcast_base", node=PodcastConfig)

def create_podcast_group(cfg: ConversationConfig):
    initializer = autogen.UserProxyAgent(
        name="init", 
        code_execution_config=False,
    )
    # create research_agents: research_coder, executor, informer
    research_agents = agent_registry.get_class("dialogue.research")(
        cfg.llm_config, cfg.system_prompts)
    podcast_host, podcast_guests = agent_registry.get_class("podcast.characters")(cfg)
    script_parser = agent_registry.get_class("podcast.parser")(
        cfg.llm_config, cfg.system_prompts)
    # create podcast agents:  podcast_host, podcast_guests
    all_agents = [initializer] + research_agents + podcast_host + podcast_guests + script_parser
    groupchat = autogen.GroupChat(
        agents=all_agents,
        messages=[],
        max_round=cfg.podcast_config.n_rounds,
        speaker_selection_method=get_state_transition(
            cfg.podcast_config, transition="podcast.default", MAX_ROUND=10
        ),
    )
    return initializer, autogen.GroupChatManager(
        groupchat=groupchat, 
        llm_config=cfg.llm_config.model_dump()
    )
