import os
import dotenv
import logging
import time
from typing import Generator
from elevenlabs import Voice
import pytest

from ficast.dialogue.clients import APIClient
from ficast.dialogue.speech import TextToSpeech

# Load environment variables
load_env = dotenv.load_dotenv("tests/.env")
assert load_env

# Configure logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture
def api_client():
    assert os.getenv("TTS_API_BASE_URL")
    return APIClient(
        base_url=os.getenv("TTS_API_BASE_URL"))


@pytest.fixture
def text_to_speech_elevenlabs():
    return TextToSpeech(
      client_type="elevenlabs", api_key=os.getenv("ELVENLABS_API_KEY"))

@pytest.fixture
def text_to_speech_api():
    return TextToSpeech(
      client_type="api", base_url=os.getenv("TTS_API_BASE_URL")
      )

def test_n_voices_elevenlabs(text_to_speech_elevenlabs):
    n_voices = text_to_speech_elevenlabs.n_voices
    assert isinstance(n_voices, int)
    assert n_voices > 0, "No voices found"
    
def test_n_voices_api(text_to_speech_api):
    n_voices = text_to_speech_api.n_voices
    assert isinstance(n_voices, int)
    assert n_voices > 0, "No voices found"

def test_get_voice_elevenlabs(text_to_speech_elevenlabs):
    voice = text_to_speech_elevenlabs.get_voice(
      voice_id=os.getenv("ELEVENLABS_VOICE_ID"))
    assert isinstance(voice, Voice), "Voice is not an instance of Voice"
    
def test_get_voice_api(text_to_speech_api):
    voice = text_to_speech_api.get_voice(
      voice_id=os.getenv("TTS_API_VOICE_ID"))
    assert isinstance(voice, str)

def test_synthesize_elevenlabs(text_to_speech_elevenlabs):
    audio = text_to_speech_elevenlabs.synthesize(
      text="Hello, World!", voice_id=os.getenv("ELEVENLABS_VOICE_ID"))
    assert isinstance(audio, Generator)

def test_synthesize_api(text_to_speech_api):
    audio = text_to_speech_api.synthesize(
      text="Hello, World!", 
      oice_id=os.getenv("TTS_API_VOICE_ID"))
    assert isinstance(audio, Generator)

