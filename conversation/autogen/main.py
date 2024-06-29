import hydra
from omegaconf import DictConfig
from autogen import GroupChat, GroupChatManager
from podcast_app.agents import create_host_agent, create_guest_agents, create_coder_agent, create_guest_agents_from_list
from podcast_app.utils import weighted_choice, state_transition

@hydra.main(config_path="conf", config_name="default.v2.0")
def main(conf: DictConfig):
    llm_config = conf.llm_config
    characters = conf.characters

    host = create_host_agent(llm_config)
    guest_conf = conf.guest_conf
    guest_agents = create_guest_agents(guest_conf)
    coder = create_coder_agent(llm_config)
    podcast_agents = create_guest_agents_from_list(llm_config, characters)

    groupchat = GroupChat(
        agents=[host, coder] + guest_agents + podcast_agents,
        messages=[],
        max_round=5,
        speaker_selection_method="round_robin"
    )

    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    characters_str = ",".join(characters)
    chat_result = host.initiate_chat(
        manager, message=f"Carry out a podcast among the characters: {characters_str}, in a real-life conversation using current and historical news to provide context. A character should only start or respond to the existing conversation."
    )

    print(chat_result.chat_history[-1])

if __name__ == "__main__":
    main()
