import os
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf
from hydra import compose, initialize, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra


from thought_agents.ontology.config.dialogue import ConversationConfig, PodcastConfig #

default_cfg = None  # Initialize as None to avoid premature loading
default_cfg_path = os.getenv(
    "HYDRA_CONFIG_PATH", "../conf/dialogue")
default_cfg_name = os.getenv(
    "HYDRA_CONFIG_NAME", "default")
def load_podcast_config(
    config_path=default_cfg_path,
    config_name=default_cfg_name
    ) -> ConversationConfig:
    print(f"Loading config version: {config_name} from path: {config_path}")
    with initialize(
        config_path=config_path, version_base="1.1"):
        config = compose(config_name=config_name)
        default_cfg = ConversationConfig(
            **OmegaConf.to_container(config, resolve=True)
        )
    return default_cfg
  
# default_llm_config  = default_cfg.llm_config
# default_system_prompts = default_cfg.system_prompts
# default_podcast_config = default_cfg.podcast_config