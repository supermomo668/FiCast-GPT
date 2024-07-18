import autogen

from thought_agents.dialogue.chat import create_podcast_group
from thought_agents.dialogue.initiator import initiation_registry
from thought_agents.dialogue.agents import agent_registry

from .config import ConversationConfig

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
