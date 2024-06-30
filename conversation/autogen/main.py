import os
from pathlib import Path
import hydra
from omegaconf import DictConfig
from .agents import create_agents

from pathlib import Path
import autogen
from conversation.autogen.management import create_groupchat


@hydra.main(config_path="conf", config_name="rag2.0")
def main(config: DictConfig):
    os.chdir(Path(__file__).resolve().parent.parent.parent)
    print(f"Chdir Home:{Path.cwd()}")
    agents = create_agents(config)
    groupchat = create_groupchat(agents, config)
    
    manager = autogen.GroupChatManager(
        groupchat=groupchat, llm_config=config.llm_config)
    
    initializer = next(agent for agent in agents if agent.name == "Init")
    characters_str = ",".join(config.characters)
    chat_result = initializer.initiate_chat(
        manager, message=f"Carry out a podcast among the characters: {characters_str}, in a real-life conversation using current and historical news to provide context. A character should only start or respond to the existing conversation."
    )
    
    print(chat_result.chat_history[-1])

if __name__ == "__main__":
    main()
