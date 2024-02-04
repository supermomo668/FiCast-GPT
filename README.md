# podcast-gpt

A Python package for processing &amp; producing podcasts using GPT

[![Python Package Test Publish](https://github.com/supermomo668/podcast-gpt/actions/workflows/python-publish.yml/badge.svg?branch=master)](https://github.com/supermomo668/podcast-gpt/actions/workflows/TestPyPi.yml)


## Install from Test PyPI

```
python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ podcast-gpt
```
## Quickstart

```
from podcast_gpt.chatbot import Chatbot
from podcast_gpt.conversation import Conversation

# Define conversation configuration
# Assuming 'conv_conf' and 'podcaster' are defined elsewhere and compatible with this setup

# Initialize chatbot instances
podcast_expert1 = Chatbot(
  "PodcastExpert1", conv_conf, conversation_type="PODCAST_GUEST")
podcast_expert2 = Chatbot(
  "PodcastExpert2", conv_conf, conversation_type="PODCAST_HOST")

# Create a conversation and add both chatbots
conversation = Conversation()
conversation.add(podcast_expert1)
conversation.add(podcast_expert2)

# Start the conversation
conversation.to_podcast()

# Print conversation history
for entry in conversation.get_history():
    print(f"{entry[0]} said: {entry[1]} | Response: {entry[2]}")

```