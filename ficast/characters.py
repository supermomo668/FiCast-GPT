from agents.ontology.dialogue.config import PodcastConfig

class podcaster:
    def __init__(self, name: str, config: PodcastConfig, conversation_type: str = "PODCAST"):
        self.name = name
        self.config = config
        self.conversation_type = conversation_type
    
    def introduce(self):
        return f"{self.name} is ready for a {self.conversation_type} conversation."
