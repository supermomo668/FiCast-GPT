import random
from typing import List

def weighted_choice(characters: List[str], current: str, weight: float = 0.5) -> str:
    return random.choices(
        [char for char in characters if char != current],
        weights=[weight if i == (characters.index(current) + 1) % len(characters) else (1 - weight) / (len(characters) - 2) for i, char in enumerate(characters) if char != current]
    )[0]

def state_transition(last_speaker, groupchat, characters, weighted_choice):
    messages = groupchat.messages

    if last_speaker.name == "Init":
        return "Retrieve_coder"
    elif last_speaker.name == "Retrieve_coder":
        return "Retrieve_executer"
    elif last_speaker.name == "Retrieve_executer":
        if messages[-1]["content"] == "exitcode: 1":
            return "Retrieve_coder"
        else:
            return "information"
    elif last_speaker.name == "information":
        return "Podcast Host"
    elif last_speaker.name in characters:
        return weighted_choice(last_speaker.name, weight=0.5)
