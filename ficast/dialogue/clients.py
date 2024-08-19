from collections.abc import AsyncGenerator
from pathlib import Path
import os, warnings, time
from typing import List, Generator, Dict
from functools import lru_cache
import warnings

import random
import json
from fastapi import HTTPException
import httpx
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed, retry_if_exception_type

import gender_guesser.detector as gd
from elevenlabs.client import ElevenLabs, AsyncElevenLabs
from elevenlabs import VoiceSettings, Voice
import tqdm

from ficast.dialogue.config import MAX_RETRY, WAIT_BETWEEN_RETRY

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
    TASK_PENDING_CODES = ('PENDING', 'STARTED', 'QUEUED')
    TASK_SUCCESS_CODES = ('SUCCESS',)
    TASK_FAILURE_CODES = ('FAILURE', 'ERROR')
    class TaskNotReadyError(Exception):
        """Custom exception raised when the task status is neither SUCCESS nor FAILURE."""
        pass
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
        # Verify the API token
        if not self.verify_token():
            raise PermissionError("Token verification failed. Please check your API key.")
        else:
            print("Token verification successful.")
            
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
    def verify_token(self):
        try:
            response = self.client.get("/verify-token")
            return response.status_code == 200 and response.json().get("message") == "true"
        except httpx.RequestError as e:
            print(f"An error occurred while trying to verify the token: {e}")
            return False
    
    def _create_tts_task(
        self, payload: dict, create_task_endpoint="/tts", **kwargs
    ):
        # create task
        task_response = self.client.post(
            create_task_endpoint, json=payload
        )
        task_response.raise_for_status()
        task_id = task_response.json().get("task_id")
        if not task_id:
            raise ValueError("Task ID not found in response.")
        return task_id

    def _get_task_status(self, task_id: str, status_endpoint="/task-status", **kwargs) -> str:
        response = self.client.get(f"{status_endpoint}/{task_id}")
        response.raise_for_status()
        status = response.json().get("status")
        if not status:
            raise ValueError("Status not found in response.")
        return status
    
    @retry(
        stop=stop_after_attempt(MAX_RETRY),
        wait=wait_fixed(WAIT_BETWEEN_RETRY),
        retry=retry_if_exception_type(TaskNotReadyError),
        reraise=True
    )
    def _wait_for_task_completion(
        self, task_id: str, status_endpoint="/task-status", **kwargs):
        """Waits for the task to reach SUCCESS or FAILURE status."""
        while True:
            status = self._get_task_status(task_id, status_endpoint)
            if status == 'SUCCESS':
                return
            elif status == 'FAILURE':
                print(f"Task {task_id} failed.")
                if kwargs.get("ignore_errors"):
                    warnings.warn(
                        "`ignore_errors=True` is set. Returning empty output.", UserWarning
                    )
                    yield b""
                raise RuntimeError(f"Task {task_id} failed.")
            else:
                raise self.TaskNotReadyError(f"Task {task_id} is not ready. Current status: {status}")

    @retry(
        stop=stop_after_attempt(MAX_RETRY),
        wait=wait_fixed(WAIT_BETWEEN_RETRY),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    def _get_task_result(
        self, task_id: str, stream:bool, result_endpoint="/task-result") -> Generator[bytes, None, None]:
        print(f"Polling for result for task...")
        try:
            with self.client.stream("GET", f"{result_endpoint}/{task_id}") as response:
                if stream:
                    for chunk in tqdm.tqdm(
                        response.iter_bytes(), desc="Streaming result..."):
                        yield chunk
                else:
                    all_bytes = b''.join(chunk for chunk in response.iter_bytes())
                    yield all_bytes
        except Exception as e:
            error_message = f"Failed to retrieve the result for task ID {task_id}: {str(e)}"
            print(error_message)
            raise HTTPException(
                status_code=500, detail=error_message)
            
    def text_to_speech(
        self, text: str, voice: str, stream:bool=False,
        create_task_endpoint="/tts", status_endpoint="/task-status", result_endpoint="/task-result",
        **kwargs
        ) -> Generator[bytes, None, None]:
        """
        Generates a speech audio stream from the given text using the specified voice.
        Args:
            text (str): The text to be converted to speech.
            voice (str): The name of the voice to use for speech generation.
            endpoint_create_task(str): endpoint to create task
            endpoint_result(str): endpoint to retrieve result
            **kwargs: Additional keyword arguments.
                preset (str, optional): The preset to use for speech generation. Defaults to "fast".
        """
        # API client uses name as voice key
        if isinstance(voice , str) and voice in ["random", "any"]:
            voice = random.choice(self.all_voices)
        payload = {
            "text": text,
            "voice": voice.name,
            "preset": kwargs.get("preset", "fast")
        }
        # Step 1: Create the task
        task_id = self._create_tts_task(
            payload, create_task_endpoint, **kwargs)
        print("Task created: ", task_id)
        # Step 2: Wait for task completion
        self._wait_for_task_completion(
            task_id, status_endpoint, **kwargs)
        # Step 3: Retrieve the task result as a stream
        yield from self._get_task_result(
            task_id, stream, result_endpoint)
    
    
    def _get_queue_status(self):
        response = self.client.get("/queue-status")
        response.raise_for_status()
        return response.json()