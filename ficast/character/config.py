from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra

from thought_agents.ontology.config.dialogue import ConversationConfig, PodcastConfig # 

with initialize(
  config_path="../../conf/dialogue", version_base="1.1"
  ):
  config = compose(config_name="default")
  # Convert the OmegaConf config to the Pydantic model
  default_cfg: ConversationConfig = ConversationConfig(
    **OmegaConf.to_container(config, resolve=True)
  )
  
default_llm_config  = default_cfg.llm_config
default_system_prompts = default_cfg.system_prompts
default_podcast_config = default_cfg.podcast_config