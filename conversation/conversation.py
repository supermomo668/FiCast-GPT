# Hold Conversation on a given episodic topic of longevity & aging between a podcaster and a human expert on a specific topic

# Import necessary libraries
from typing import List
import yaml
from mutagen.mp3 import MP3
from . import DEFAULT_CONF
  
class BaseConv:
  def __init__(self, name):
      self.name = name

  def __init__(self, conf=DEFAULT_CONF):
    """
    Initialize the Conversation class.
    """
    self.conversation = []
    self.conf = conf

  def reset_conversation(self) -> None:
    """
    Reset the conversation history.
    """
    self.conversation = []

  def add_to_conversation(self, response: str) -> None:
    """
    Add a response to the conversation history.
    """
    self.conversation.append(response)

  def _get_conversation(self) -> List[str]:
    """
    Return the conversation history.
    """
    return self.conversation

class RoundTable(BaseConv):
    def __init__(self, conf):
        """
        one-size-fit-all configuration for the conversation
        """
        self.participants = []

    def add(self, chatbot):
        """Add a chatbot to the conversation."""
        if isinstance(chatbot, Chatbot):
            self.participants.append(chatbot)
        else:
            raise ValueError("Only Chatbot instances can be added to the conversation.")    

    def show_participants(self):
        """List all participants in the conversation."""
        return ', '.join(
          [bot.name for bot in self.participants]
        )
    
    def start(self):
        """Create a podcast from the conversation."""
        assert len(self.participants) > 0, "No participants in the conversation."
        for bot in self.participants:
          bot.create_podcast()
  
    def _conversation(self):
        """Simulate a conversation between all participants in the conversation."""
        

    def send_message(self, from_bot, message):
        """Simulate sending a message from one bot to all other bots in the conversation."""
        if from_bot not in self.participants:
            raise ValueError(f"{from_bot.name} is not a participant in this conversation.")

        print(f"{from_bot.name} says: {message}")
        for bot in self.participants:
            if bot != from_bot:
                reply = bot.reply(message)
                print(f"{bot.name} replies with: {reply}")

if __name__ == "__main__":
    # Create chatbot instances
    chatbot1 = Chatbot("Alice")
    chatbot2 = Chatbot("Bob")

    # Initialize a conversation
    conversation = Conversation()

    # Add chatbots to the conversation
    conversation.add(chatbot1)
    conversation.add(chatbot2)

    # List participants
    print("Participants:", conversation.show_participants())

    # Simulate a message exchange
    conversation.send_message(chatbot1, "How are you?")
    # Add logic here for chatbot2 to respond, and potentially for chatbot1 to reply back



