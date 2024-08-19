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
  podcast_dict_cfg = OmegaConf.to_container(config, resolve=True)
  conv_cfg: ConversationConfig = ConversationConfig(**podcast_dict_cfg)
  

# Register the configuration with ConfigStore
cs = ConfigStore.instance()
cs.store(name="podcast_config", node=podcast_dict_cfg)