from collections.abc import AsyncGenerator
from pathlib import Path
import os
from typing import List, Generator, Dict
from functools import lru_cache
from fastapi import requests
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
      
class APIClient(BaseTTSClient):
    def __init__(self, base_url: str=None, api_key: str = None):
        if not base_url:
            base_url = os.getenv('TTS_API_BASE_URL')
            assert base_url, "API base URL must be provided for FiCastTTS client or set the `TTS_API_BASE_URL` environment variable with your base URL"
        if not api_key: 
            api_key = os.getenv('TTS_API_KEY')
        assert api_key, "API key must be provided for FiCastTTS client or set the `TTS_API_KEY` environment variable with your API key"
        self.client = httpx.Client(
            base_url=base_url, 
            timeout=httpx.Timeout(40.0, connect=60.0),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('TTS_API_KEY')}"
            }
        )
        if not self.ping():
            raise ConnectionError("Ping check failed. The TTS service is not available.")
    @property
    @lru_cache(maxsize=None)
    def all_voices(self) -> List[Voice]:
        """
        Returns a list of all available voices.
        Returns:
            List[Voice]: A list of `Voice` objects representing all available voices.
        """
        gender_detector = gd.Detector()
        voice_names = self.client.get(f"/voices").json()["voices"]
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
    def ping(self) -> bool:
        try:
            response = self.client.get("/ping")
            try:
                response.raise_for_status()
            except httpx.RequestError as exc:
                raise httpx.RequestError(f"An error occurred while requesting {exc.request.url!r}.") from exc
            return response.status_code == 200 and response.json().get("status") == "ok"
        except Exception as e:
            return False
        
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
        # API client uses name as voice key
        payload = {
            "text": text,
            "voice": voice.name,
            "preset": kwargs.get("preset", "fast")
        }
        task_response = self.client.post(
            f"/tts", json=payload
        )
        task_response.raise_for_status()
        if "task_id" in task_response.json():
            task_id = task_response.json()["task_id"]
        else:
            raise ValueError(f"Task cannot be created: {task_response.json()}")
        # Post the result
        long_timeout = httpx.Timeout(300.0, connect=60.0)  # Adjust the timeout as needed
        result_response = self.client.get(
            f"/task-result/{task_id}", 
            timeout=long_timeout
        )
        result_response.raise_for_status()
        for chunk in result_response.iter_bytes():
            yield chunk

    def get_queue_status(self):
        response = self.client.get("/queue-status")
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id: str):
        response = self.client.get(f"/task-status/{task_id}")
        response.raise_for_status()
        return response.json()