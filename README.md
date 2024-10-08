# FiCast (formly FiCast-GPT)

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
* Installing from Test PyPI using poetry:
  ```
  poetry add ficast-gpt --source https://test.pypi.org/simple/
  ```
* Required environment / keys configuration
  1. `conf/OAI_CONFIG_LIST.txt` following the syntax of [PyAutogen](https://github.com/microsoft/autogen), the framework this package is based on to configure your LLM clients.
      * Note: Please add the followin safety settings to the model configuration to avoid safety-related filter errors during generation.
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
  2. ElevenLabs Transcription API Key in `.env` as such (see [example](.example.env))
      ```
      ELEVENLABS_API_KEY=<Your_Elevelabs_API_Key>
      ```
      Optionally, you could [use Tortoise-TTS for Local Inference](#optional-using-tortoise-tts-for-local-inference). This set-up is more complex and is currently under development.
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

## Managing Git Submodules

This repository contains submodules for two key components of the FiCast project:

1. **FiCast Web Frontend**: The web frontend for FiCast is located in the `apps/web` directory and is a separate repository hosted privately at [FiCast-Frontend](https://github.com/supermomo668/FiCast-Frontend).
2. **Tortoise-TTS**: The text-to-speech (TTS) engine is located in the `tortoise-tts` directory and is hosted as a separate submodule.

  ### Cloning the Repository with Submodules

  When cloning this repository for the first time, you need to initialize the submodules to ensure you get the content for both `apps/web` and `tortoise-tts`.

  Run the following commands to clone the repository and initialize the submodules:

  ```bash
  git clone git@github.com:supermomo668/FiCast-GPT.git
  cd FiCast-GPT
  git submodule update --init --recursive
  ```

  This will ensure that both the FiCast Web Frontend (`apps/web`) and Tortoise-TTS (`tortoise-tts`) submodules are correctly fetched.

## Autogen Workflow Diagram (An Illustration of how the conversation takes place)

<p align="center">
  <img src="https://www.mermaidchart.com/raw/62a04ff4-da63-4033-a610-a2aacc5fba5c?theme=light&version=v0.1&format=svg" width="100%">
</p>


## Optional: Using Tortoise-TTS for Local Inference

If you prefer to use the Tortoise-TTS for local inference instead of the ElevenLabs API, you need to pull the `tortoise-tts` submodule. Follow the instructions below to set it up.

### [Alternative] Steps to Pull the Tortoise-TTS Submodule

- **Only the commands if you need the submodule:**

1. **Initialize and Update the Submodule:**

    ```sh
    git submodule init
    git submodule update
    ```

2. **Clone the Submodule Directly (if not already cloned):**

    ```sh
    git submodule add https://github.com/neonbjb/tortoise-tts.git path/to/tortoise-tts
    ```

3. **Setup Tortoise-TTS for Inference:**
   
    Follow any additional setup instructions provided in the `tortoise-tts` repository to complete the configuration for local inference.

### Important: What NOT to Do If Not Using the Submodule

If you do not need to use the Tortoise-TTS submodule for local inference, **do not** run the submodule initialization and update commands. Additionally, you can avoid pulling the submodule by skipping the steps mentioned above.


## Contributing

Guidelines for contributing to the project.

## License

Apache 2.0
