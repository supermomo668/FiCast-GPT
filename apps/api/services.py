import os
from .models import PodcastRequest
from ficast.character.podcast import Podcaster
from ficast.conversation.podcast import Podcast
from ficast.assembly.ficast import FiCast
from ficast.dialogue.speech import DialogueSynthesis
from datetime import datetime
from typing import Dict, Any

def generate_podcast_script(request: PodcastRequest) -> Dict[str, Any]:
    # Initialize the Podcast object
    my_podcast = Podcast(topic=request.topic, n_rounds=request.n_rounds)

    # Add participants to the podcast
    participants = []
    for participant in request.participants:
        podcaster = Podcaster(
            name=participant.name,
            description=participant.description,
            model=participant.model,
            role=participant.role if participant.role else "guest"
        )
        participants.append(podcaster)

    my_podcast.add(participants)

    # Generate and return the podcast script
    return my_podcast.json_script

def generate_podcast_audio(request: PodcastRequest) -> bytes:
    # Initialize the Podcast object
    my_podcast = Podcast(
      topic=request.topic, 
      n_rounds=request.n_rounds
    )

    # Add participants to the podcast
    participants = []
    for participant in request.participants:
        podcaster = Podcaster(
            name=participant.name,
            description=participant.description,
            model=participant.model,
            role=participant.role if participant.role else "guest"
        )
        participants.append(podcaster)

    my_podcast.add(participants)

    # Generate the podcast script
    my_podcast.create()

    # Initialize the DialogueSynthesis object
    dialoguer = DialogueSynthesis(
        client_type="api",
        base_url=os.getenv("TTS_API_BASE_URL"),
        api_key=os.getenv("TTS_API_KEY")
    )

    # Assemble the podcast using FiCast
    fantasy_ficast = FiCast(
      conversation=my_podcast, dialogue_synthesizer=dialoguer)
    my_audio = fantasy_ficast.to_podcast(ignore_errors=True)

    # Convert the byte stream to a .wav file format
    from ficast.dialogue.utils import save_bytes_to_wav
    audio_filename = f"ficast-outputs/samples/podcasts/{datetime.now()}.wav"
    save_bytes_to_wav(my_audio, audio_filename)

    # Return the byte stream for the generated podcast audio
    return my_audio
