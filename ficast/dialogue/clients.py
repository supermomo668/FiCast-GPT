from collections.abc import AsyncGenerator
from pathlib import Path
import os
from typing import List, Generator, Dict
from functools import lru_cache
import gender_guesser.detector as gd

import random
import json
import httpx

from elevenlabs.client import ElevenLabs, AsyncElevenLabs
from elevenlabs import VoiceSettings, Voice

from .utils import CustomJSONEncoder
from .base import BaseTTSClient

def tts_client_factory(
  client_type: str = "api", base_url: str = None, api_key: str = None
  ) -> BaseTTSClient:
    if client_type.lower() == "elevenlabs":
        api_key = os.getenv("ELEVENLABS_API_KEY") if api_key is None else None
        if api_key is None:
            raise ValueError("API key must be provided for ElevenLabs client")
        return ElevenLabsClient(api_key=api_key)
    elif client_type.lower() == "api":
        if base_url is None:
            raise ValueError("Base URL must be provided for FiCastTTS client")
        return APIClient(base_url=base_url)
    else:
        raise ValueError("Unknown client type. Supported: 'api', 'elevenlabs'")
    
class ElevenLabsClient(BaseTTSClient):
    voice_settings = VoiceSettings(
        stability=random.uniform(0.3, 1), 
        similarity_boost=random.random(),
        style=random.random(),
        use_speaker_boost=True
    )
    meta_dir = Path("ficast-outputs/voice")
    def __init__(
        self, api_key: str, model="eleven_multilingual_v2"):
        self.client = ElevenLabs(api_key=api_key)
        self.model = model
        Path(self.meta_dir).mkdir(exist_ok=True, parents=True)
    
    @property
    @lru_cache(maxsize=None)
    def all_voices(self) -> List[Voice]:
        response = self.client.voices.get_all()
        return response.voices
    
    @property
    @lru_cache(maxsize=None)
    def all_voices_by_id(self, save_meta=True) -> Dict[str, dict]:
        """
        Retrieves all the voices from the API and returns a dictionary mapping voice names to their corresponding voice IDs.
        Returns:
            Dict[int, Voice]: A dictionary mapping voice names to their corresponding voice IDs.
        """
        self.voice_metainfo = [
            v.__dict__ for v in self.all_voices]
        if save_meta:
            with open(self.meta_dir / 'voice_metainfo.json', 'w') as f:
                json.dump(
                    self.voice_metainfo, f, indent=4, cls=CustomJSONEncoder)
        return {
            v.voice_id: v for v in self.all_voices}

    def text_to_speech(
        self, text: str, voice: Voice, **kwargs
        ) -> Generator[bytes, None, None]:
        audio = self.client.generate(
          text=text, voice=voice, model=kwargs.get('model', self.model))
        return audio

    def get_queue_status(self):
        # Implement if needed
        pass

    def get_task_status(self, task_id: str):
        # Implement if needed
        pass

      
class APIClient(BaseTTSClient):
    def __init__(self, base_url: str=""):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=httpx.Timeout(40.0, connect=60.0))

        try:
            response = self.client.get(f"{self.base_url}")
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise httpx.RequestError(f"An error occurred while requesting {exc.request.url!r}.") from exc
        except httpx.HTTPStatusError as exc:
            raise httpx.HTTPStatusError(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.") from exc
    @property
    @lru_cache(maxsize=None)
    def all_voices(self) -> List[Voice]:
        """
        Returns a list of all available voices.
        Returns:
            List[Voice]: A list of `Voice` objects representing all available voices.
        """
        gender_detector = gd.Detector()
        voice_names = self.client.get(f"{self.base_url}/voices").json()["voices"]
        vs = []
        for n, name in enumerate(voice_names):
            vs.append(Voice(
                voice_id=str(n), name=name, 
                labels={
                    "gender": gender_detector.get_gender(name.split(" ")[0]),
                }))
        assert len(vs) > 0
        return vs
    
    @property
    @lru_cache(maxsize=None)
    def all_voices_by_id(self) -> Dict[str, Voice]:
        """
        Returns a dictionary mapping voice IDs to Voice objects.
        """
        return {
            voice.voice_id: voice for voice in self.all_voices
        }

    def text_to_speech(
        self, text: str, voice: str, **kwargs
        ) -> Generator[bytes, None, None]:
        """
        Generates a speech audio stream from the given text using the specified voice.
        Args:
            text (str): The text to be converted to speech.
            voice (str): The name of the voice to use for speech generation.
            **kwargs: Additional keyword arguments.
                preset (str, optional): The preset to use for speech generation. Defaults to "fast".
        """
        # API client uses name instead of Voice objet
        payload = {
            "text": text,
            "voice": voice.name,
            "preset": kwargs.get("preset", "fast")
        }
        response = self.client.post(
            f"{self.base_url}/tts", json=payload,
            auth=(os.getenv("TTS_API_USERNAME"), os.getenv("TTS_API_PASSWORD"))
        )
        response.raise_for_status()
        for chunk in response.iter_bytes():
            yield chunk

    def get_queue_status(self):
        response = self.client.get(f"{self.base_url}/queue-status")
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id: str):
        response = self.client.get(f"{self.base_url}/task-status/{task_id}")
        response.raise_for_status()
        return response.json()