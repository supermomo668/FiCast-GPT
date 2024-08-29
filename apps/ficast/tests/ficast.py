import pytest
from hydra import initialize, compose
from omegaconf import OmegaConf
from ficast.config import default_cfg, ConversationConfig

def test_hydra_config_load():
    # Test if the default configuration loads correctly
    with initialize(
      config_path="../../../conf/dialogue", version_base="1.1"):
        config = compose(config_name="default")
        assert config is not None
        # Optionally verify specific configurations
        assert "system_prompts" in config
        # Verify that the default configuration is correctly converted to a Pydantic model
        assert default_cfg is not None
        assert isinstance(
          default_cfg, ConversationConfig)