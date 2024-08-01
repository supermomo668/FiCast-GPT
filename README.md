# FiCast-gpt

A Python package for processing &amp; producing PodCast overlayed with music aligned to the podcast :  "Fi-Casts" (LoFi + Podcast) 

[![Test PyPi](https://github.com/supermomo668/podcast-gpt/actions/workflows/TestPyPi.yml/badge.svg?branch=main)](https://github.com/supermomo668/podcast-gpt/actions/workflows/TestPyPi.yml)

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Optional: Using Tortoise-TTS for Local Inference](#optional-using-tortoise-tts-for-local-inference)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Tool for processing & producing musical podcasts w/ thoughtful multi-agents

## Installation

* Installing from Test PyPI
  ```
  python3 -m pip install -i https://test.pypi.org/simple/ ficast-gpt
  ```
* Required environment / keys configuration
  You must set up conf/OAI_CONFIG_LIST.txt following the syntax of [PyAutogen](https://github.com/microsoft/autogen), the framework this package is based on to configure your LLM clients.
  * Note:
    Please add the followin safety settings to the model configuration to avoid safety-related filter errors during generation.
    ```
    "safety_settings": [
      {
          "category": "HARM_CATEGORY_HARASSMENT",
          "threshold": "BLOCK_NONE"
      },
      {
          "category": "HARM_CATEGORY_HATE_SPEECH",
          "threshold": "BLOCK_NONE"
      },
      {
          "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
          "threshold": "BLOCK_NONE"
      },
      {
          "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
          "threshold": "BLOCK_NONE"
      }
      ]
      ```

## Usage

* Environment

Check out the [tutorial notebook](notebook/quickstart.ipynb) for the following example.

```python
from ficast.character.podcast import Podcaster
from ficast.conversation.podcast import Podcast

my_podcast = Podcast(
  # define podcast topic
  topic="health & longevity", 
  # define number of rounds
  n_rounds=20, 
)

# Initialize participant instances
joe_rogan = Podcaster(
  name="Joe Rogan", 
  description="Joe Rogan is a funny and popular podcast host",
  model="gpt-3.5-turbo",
  role="host"
)
david_sinclair = Podcaster(
  name="David Sinclair",
  description="David Sinclair is a Harvard Medical Expert",
  model="gpt-3.5-turbo"
  # default role as a guest
)

# Aadd both podcast participants to conversation
my_podcast.add([joe_rogan, david_sinclair])

# Create the podcast dialogues
my_script = my_podcast.create()

# check the scripts
# raw string script
my_podcast.raw_script
# return chat history from script (warning: this part can fail due to the inconsistency of formatting that may result from individual dialogues from the LLMs)
my_podcast.script
# a structured json script parsed 
my_podcast.json_script

from ficast.assembly.ficast import FiCast
fantasy_ficast = FiCast(conversation=my_podcast)

# Convert the conversation to an audio podcast
my_audio = fantasy_ficast.to_podcast()

# Save / Play Audio!
from datetime import datetime
fantasy_ficast.save_podcast()

# play audio
from elevenlabs import play
play(bytes(my_audio, 'latin-1'))
```

## Declaritive Configruation [In Development. Status: N/A]

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

## Autogen Workflow Diagram

<p align="center">
  <img src="https://www.mermaidchart.com/raw/62a04ff4-da63-4033-a610-a2aacc5fba5c?theme=light&version=v0.1&format=svg" width="60%">
</p>


## Optional: Using Tortoise-TTS for Local Inference

If you prefer to use the Tortoise-TTS for local inference instead of the ElevenLabs API, you need to pull the `tortoise-tts` submodule. Follow the instructions below to set it up.

### [Alternative] Steps to Pull the Tortoise-TTS Submodule

1. **Initialize and Update the Submodule:**

    ```sh
    git submodule init
    git submodule update
    ```

2. **Clone the Submodule Directly (if not already cloned):**

    ```sh
    git submodule add https://github.com/neonbjb/tortoise-tts.git path/to/tortoise-tts
    ```

3. **Install Tortoise-TTS Dependencies:**

    ```sh
    cd path/to/tortoise-tts
    pip install -r requirements.txt
    ```

4. **Setup Tortoise-TTS for Inference:**
   
    Follow any additional setup instructions provided in the `tortoise-tts` repository to complete the configuration for local inference.

### Important: What NOT to Do If Not Using the Submodule

If you do not need to use the Tortoise-TTS submodule for local inference, **do not** run the submodule initialization and update commands. Additionally, you can avoid pulling the submodule by skipping the steps mentioned above.

- **Do not run the following commands if you do not need the submodule:**

    ```sh
    git submodule init
    git submodule update
    git submodule add https://github.com/neonbjb/tortoise-tts.git path/to/tortoise-tts
    ```

By following these guidelines, you can ensure that your repository is set up correctly whether or not you choose to use the Tortoise-TTS submodule for local inference.

## Contributing

Guidelines for contributing to the project.

## License

Apache 2.0