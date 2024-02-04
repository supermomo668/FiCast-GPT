# podcast-gpt

A Python package for processing &amp; producing podcasts using GPT

[![Test PyPi](https://github.com/supermomo668/podcast-gpt/actions/workflows/TestPyPi.yml/badge.svg?branch=main)](https://github.com/supermomo668/podcast-gpt/actions/workflows/TestPyPi.yml)


## Install from Test PyPI

```
python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ podcast-gpt
```
## Quickstart

```python
from podcast_gpt.agent import podcaster
from podcast_gpt.conversation import Conversation

# Define conversation configuration
# Assuming 'conv_conf' and 'podcaster' are defined elsewhere and compatible with this setup

# Initialize chatbot instances
joe_rogan = podcaster(
  "Joe Rogan", conv_conf, conversation_type="PODCAST")
harvard_david_sinclair = podcaster(
  "Harvard Medical Expert", conv_conf, conversation_type="PODCAST")

# Create a conversation and add both chatbots
conversation = Conversation()
conversation.add(joe_rogan)
conversation.add(harvard_david_sinclair)

# Make a podcast conversation
audio = conversation.to_podcast()
```

## Conversation & Music Configruation

>```yaml
MODEL: gpt-4
PROMPTS: 
  AGENTS:
    DEFAULT: "The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:"
    PODCAST_HOST: "The following is a friendly conversation between a passionate podcast host and a Harvard medical expert. The host is and knowledgeable in the health/longevity biotech & biology space. The host provides questions and talking points based in academic research and entrepreneurship space, akin to Andrew Hubermann, Simon Hill and David Sinclair and will also respond to the guest's response .\n\nCurrent conversation:\n{history}\nSystem:{input}\nPodcast Host:"
    PODCAST_GUEST(HARVARD): "The following is a friendly conversation between a passionate podcast host and a Harvard medical expert. The guest expert is particularly knowledgeable in the health/longevity biotech & biology space that could reference academic research and entrepreneurship space, akin to Andrew Hubermann, Simon Hill and David Sinclair. The host provides questions and talking points while the guest provides fully elaborated responses to the host's questions.\n\nCurrent conversation:\n{history}\nPodcast Host: {input}\nExpert:"
    PODCAST_GUEST: "The following is a friendly conversation between a passionate podcast host and a Harvard medical expert. The guest expert is particularly knowledgeable in the health/longevity biotech & biology space that could reference academic research and entrepreneurship space, akin to Andrew Hubermann, Simon Hill and David Sinclair. As the guest expert, you provide detailed, insigthful & comprehensive responses to the host's questions.\n\nCurrent conversation:\n{history}\nPodcast Host: {input}\nExpert:"
  CONVERSATION:
    HOST_CONTINUATION: Apart from what you mentioned, would you mind elaborating on what you discussed and some additional adjacent concepts?
MEMORY_CONTEXT_TOKEN: 2000
WORDS_PER_MIN: 150
SPEAKING_TIME_MINS: 60
```
