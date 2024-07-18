from agents.ontology.dialogue.config import PodcastConfig, AutogenLLMConfig, PodcastCharacters, Person
from .characters import podcaster
from .conversation import Conversation

class Assembly:
    def __init__(self, config: PodcastConfig, conversation: Conversation):
        self.config = config
        self.conversation = conversation
    
    def inject_music(self, music_type: str):
        # Add logic to inject music into the podcast
        print(f"Injecting {music_type} music into the podcast.")
        return self
    
    def to_podcast(self):
        # Finalize and return the podcast conversation
        return f"Podcast with participants:\n{self.conversation.start()}"
