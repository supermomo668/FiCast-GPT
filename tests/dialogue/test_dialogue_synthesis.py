import dotenv, os
from elevenlabs import Voice
from pydantic import GenerateSchema
from typing import Generator
from unittest.mock import patch, Mock

import pytest
import warnings
from ficast.dialogue.speech import DialogueSynthesis

# Load environment variables
load_env = dotenv.load_dotenv("tests/.env")
assert load_env

@pytest.fixture
def mock_tts_client():
    client_mock = Mock()
    client_mock.text_to_speech.return_value = (
      chunk for chunk in [b'audio_chunk1', b'audio_chunk2'])
    client_mock.all_voices_by_id = {
        '1': Mock(
          name='Voice1', labels={'gender': 'male'}),
        '2': Mock(name='Voice2', labels={
          'gender': 'female'}),
        '3': Mock(name='Voice3', labels={'gender': 'andy'})
    }
    return client_mock
  
@pytest.fixture
def dialogue_synthesis_elevenlabs():
    return DialogueSynthesis(client_type="elevenlabs")

@pytest.fixture
def dialogue_synthesis_api():
    return DialogueSynthesis(
      client_type="api", 
      base_url=os.getenv("TTS_API_BASE_URL"))

def test_get_nth_voice_by_gender_elevenlabs(dialogue_synthesis_elevenlabs):
    voice = dialogue_synthesis_elevenlabs.get_nth_voice_by_gender(nth=0, gender='male')
    assert isinstance(voice, Voice), "Returned voice is not a dictionary"
    assert voice.labels["gender"] == 'male', "The returned voice is not male"

def test_get_nth_voice_by_gender_api(dialogue_synthesis_api):
    voice = dialogue_synthesis_api.get_nth_voice_by_gender(nth=0, gender=None)
    assert isinstance(voice, Voice), "Returned voice is not a Voice object"
    assert voice.labels["gender"] is not None

def test_get_nth_voice_by_gender_out_of_range(dialogue_synthesis_api):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        voice = dialogue_synthesis_api.get_nth_voice_by_gender(nth=100, gender="female")
        assert len(w) > 0, "Warning was not triggered for out-of-range nth"
        assert issubclass(w[-1].category, UserWarning), "Warning was not a UserWarning"
    assert isinstance(voice, Voice), "Returned voice is not a Voice object"
    assert voice.labels["gender"].lower() in ["female", "unknown"], "The returned voice is not andy"

def test_invalid_gender(dialogue_synthesis_elevenlabs):
  with pytest.raises(
    AssertionError, match="Not a supported gender"):
    dialogue_synthesis_elevenlabs.get_nth_voice_by_gender(nth=0, gender='invalid_gender')

@pytest.fixture
def dialogue_synthesis(mock_tts_client, monkeypatch):
    monkeypatch.setattr(
      'ficast.dialogue.speech.tts_client_factory', lambda client_type, **kwargs: mock_tts_client)
    return DialogueSynthesis(client_type='elevenlabs')
  
def test_synthesize_dialogue_synthesis(dialogue_synthesis):
    text = "Hello, World!"
    voice_id = '2'
    audio_generator = dialogue_synthesis.synthesize(text, voice_id)
    assert isinstance(audio_generator, Generator)
    audio_chunks = list(audio_generator)
    assert audio_chunks == [b'audio_chunk1', b'audio_chunk2']
