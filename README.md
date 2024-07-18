# FiCast-gpt

A Python package for processing &amp; producing PodCast overlayed with music aligned to the podcast :  "Fi-Casts" (LoFi + Podcast) 

[![Test PyPi](https://github.com/supermomo668/podcast-gpt/actions/workflows/TestPyPi.yml/badge.svg?branch=main)](https://github.com/supermomo668/podcast-gpt/actions/workflows/TestPyPi.yml)


## Install from Test PyPI

```
python3 -m pip install -i https://test.pypi.org/simple/ ficast-gpt
```
## Quickstart

```python
from ficast.character.podcaster import Podcaster
from ficast.conversation.podcast import ConversationConfig
from ficast.assemble.ficast import FiCast, Conversation

# Define conversation configuration
conversation_config = ConversationConfig(
    llm_config=AutogenLLMConfig(),  # Placeholder for LLM configuration
    podcast_config=PodcastConfig(
        topic="democracy",
        n_rounds=20,
        character_cfg=PodcastCharacters(
            hosts=[Person(name="Joe Rogan", description="Joe Rogan is a funny and popular podcast host")],
            guests=[Person(name="David Sinclair", description="David Sinclair is a Harvard Medical Expert")]
        )
    ),
    system_prompts={}  # Placeholder for system prompts
)

# Initialize participant instances
joe_rogan = Podcaster(name="Joe Rogan", description="Joe Rogan is a funny and popular podcast host")
david_sinclair = Podcaster(name="David Sinclair", description="David Sinclair is a Harvard Medical Expert")

# Create a conversation and add both podcast participants
conversation = Conversation(type="podcast", n_rounds=20, topic="democracy", output_format="json")
conversation.add([joe_rogan.name, david_sinclair.name])

# Create a FiCast instance
my_podcast = FiCast(conversation_config, conversation)

# Inject music into the podcast
musical_podcast = my_podcast.inject_music(style="auto")

# Convert the conversation to an audio podcast
final_podcast = musical_podcast.to_podcast()
```

## Declaritive Configruation

You may choose to run the application in a one-time declartive format using the `ficast.main` module.
```yaml
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
SPEECH:
  WORDS_PER_MIN: 150

CONVERSATION:
  SPEAKING_TIME_MINS: 60
  TEMPO: 75

MUSIC:
  SOURCE: CHAOSIC
  CATEOGRY: lofi
  BPM: 80
```
