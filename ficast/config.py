from pydantic import BaseModel, Field
from typing import List, Dict, Any, AnyStr

class Person(BaseModel):
    name: AnyStr = Field(..., description="Name of the person")
    description: AnyStr = Field(..., description="1-2 line description of the person if known, otherwise just a generic character.")

class PodcastCharacters(BaseModel):
    host: Person = Field(..., description="Host of the podcast")
    guests: List[Person] = Field(..., description="List of guests of the podcast")

class AutogenLLMConfig(BaseModel):
    cache_seed: int = 42
    temperature: float = 0
    timeout: int = 120
    config_list: List = []
    filter_dict: Dict = {
        "model": ["gemini-pro"]
    }
    config_list_path: str = "conf/OAI_CONFIG_LIST.txt"

    @field_validator("config_list", mode="before")
    def initialize_config_list(cls, v, values: Dict[str, Any]) -> List:
        if v:  # If config_list is already provided, use it
            return v
        config_list = autogen.config_list_from_json(
            to_absolute_path(values.get("config_list_path", "conf/OAI_CONFIG_LIST.txt")),
            filter_dict=values.get("filter_dict", {"model": ["gemini-pro"]}),
        )
        return config_list

class PodcastConfig(BaseModel):
    llm_config: AutogenLLMConfig
    characters: PodcastCharacters
    system_prompts: Dict
