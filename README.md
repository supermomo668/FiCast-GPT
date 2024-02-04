# podcast-gpt

A Python package for processing &amp; producing podcasts using GPT

[![Test PyPi](https://github.com/supermomo668/podcast-gpt/actions/workflows/TestPyPi.yml/badge.svg?branch=main)](https://github.com/supermomo668/podcast-gpt/actions/workflows/TestPyPi.yml)


## Install from Test PyPI

```
python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ podcast-gpt
```
## Quickstart

```python
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

# Make a podcast conversation
audio = conversation.to_podcast()
```
