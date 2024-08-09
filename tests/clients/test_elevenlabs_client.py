from elevenlabs import Voice
import pytest
import dotenv, os

from typing import Generator
from ficast.dialogue.clients import ElevenLabsClient

# Load environment variables
load_env = dotenv.load_dotenv("tests/.env")
assert load_env

@pytest.fixture
def elevenlabs_client():
    return ElevenLabsClient(api_key=os.getenv("ELVENLABS_API_KEY"))

def test_get_all_voices(elevenlabs_client):
    voices = elevenlabs_client.all_voices
    assert isinstance(voices, list)

def test_get_all_voices_by_id(elevenlabs_client):
    voices_by_id = elevenlabs_client.all_voices_by_id
    assert isinstance(voices_by_id, dict)
    assert all(isinstance(k, str) and isinstance(v, Voice) for k, v in voices_by_id.items()), "All keys and values should be strings and Voice objects"

def test_text_to_speech(elevenlabs_client):
    audio = elevenlabs_client.text_to_speech(
        text="Hello, test!", voice=os.getenv("ELEVENLABS_VOICE_ID"))
    assert isinstance(audio, Generator)
    # Check that the generator produces audio chunks of type bytearray
    for chunk in audio:
        assert isinstance(chunk, bytes)
        break  # Just checking the first chunk for type validation