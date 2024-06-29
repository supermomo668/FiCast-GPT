import autogen
import random

def weighted_choice(characters, current, weight=0.5):
    return random.choices(
        [char for char in characters if char != current],
        weights=[weight if i == (characters.index(current) + 1) % len(characters) else (1 - weight) / (len(characters) - 2) for i, char in enumerate(characters) if char != current]
    )[0]

def state_transition(last_speaker, groupchat):
    messages = groupchat.messages

    if last_speaker.name == "Init":
        return groupchat.get_agent_by_name("Retrieve_coder")
    elif last_speaker.name == "Retrieve_coder":
        return groupchat.get_agent_by_name("Retrieve_executer")
    elif last_speaker.name == "Retrieve_executer":
        if messages[-1]["content"] == "exitcode: 1":
            return groupchat.get_agent_by_name("Retrieve_coder")
        else:
            return groupchat.get_agent_by_name("information")
    elif last_speaker.name == "information":
        return groupchat.get_agent_by_name("Podcast Host")
    elif last_speaker.name in [agent.name for agent in groupchat.agents if agent.name in characters]:
        return groupchat.get_agent_by_name(weighted_choice(characters, last_speaker.name, weight=0.5))

def create_groupchat(agents, config):
    return autogen.GroupChat(
        agents=agents,
        messages=[],
        max_round=5,
        speaker_selection_method="round_robin"
    )
