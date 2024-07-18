class Conversation:
    def __init__(self):
        self.participants = []
    
    def add(self, podcaster):
        self.participants.append(podcaster)
    
    def start(self):
        introductions = [p.introduce() for p in self.participants]
        return "\n".join(introductions)
