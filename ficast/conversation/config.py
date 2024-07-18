from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra

from thought_agents.ontology.config.dialogue import ConversationConfig, PodcastConfig # 

with initialize(config_path="../../conf/dialogue"):
  config = compose(config_name="default")
  # Convert the OmegaConf config to the Pydantic model
  cfg: ConversationConfig = ConversationConfig(
    **OmegaConf.to_container(config, resolve=True)
  )
  
# Register the configuration with ConfigStore
cs = ConfigStore.instance()
cs.store(name="podcast_config", node=PodcastConfig)
cs.store(name="podcast_default", node=ConversationConfig)