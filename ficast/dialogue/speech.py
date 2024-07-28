from typing import List, Generator
from abc import abstractmethod
from collections.abc import AsyncGenerator
import os, dotenv, json, pathlib
from functools import lru_cache

import random

from elevenlabs import play, voices, VoiceSettings, Voice
from elevenlabs.client import ElevenLabs, AsyncElevenLabs

from .utils import CustomJSONEncoder

dotenv.load_dotenv()

class ElevenSpeech:
  voice_settings = VoiceSettings(
    stability=random.uniform(0.3, 1), 
    similarity_boost=random.random(),
    style=random.random(),
    use_speaker_boost=True
  )
  meta_dir = pathlib.Path("ficast-outputs/dialogue")
  def __init__(self):
    self.client = ElevenLabs(
      api_key=os.environ.get("ELEVENLABS_API_KEY"),  # Defaults to ELEVEN_API_KEY
      # httpx_client=httpx.AsyncClient()
    )
    self.meta_dir.mkdir(exist_ok=True, parents=True)
    
  @property
  @lru_cache(maxsize=None)
  def all_voices(self, save_meta=True) -> List[Voice]:
    response = self.client.voices.get_all()
    self.voice_metainfo = [v.__dict__ for v in response.voices]
    print(f"Available voices:\n", self.voice_metainfo)
    if save_meta:
      with open(self.meta_dir / 'voice_metainfo.json', 'w') as f:
        json.dump(self.voice_metainfo, f, indent=4, cls=CustomJSONEncoder)
    return response.voices
  
  @property
  def n_voices(self):
    return len(self.all_voices())

  def get_voice(self, voice_id, save_meta=True):
    """
    Retrieves a voice from the list of available voices based on the provided voice ID.
    Args:
        voice_id (int): The ID of the voice to retrieve.
        save_meta (bool, optional): Whether to save the metadata of the retrieved voice. Defaults to True.
        output_dir (pathlib.Path, optional): The directory to save the metadata file. Defaults to "output/speech".
    """
    idx = [i for i, v in enumerate(self.all_voices) if v.voice_id == voice_id]
    if len(idx) == 0:
      raise ValueError(f"Voice {voice_id} not found")
    # len(idx) == 1
    idx = idx[0]
    if save_meta:
      with open(self.meta_dir / 'last_used_voice.json', 'w') as f:
        json.dump(self.voice_metainfo[idx], f, indent=4, cls=CustomJSONEncoder)
    return self.all_voices[idx]

  def synthesize(
    self,
    voice_id: int,
    text: str="Hello! 你好! Hola! नमस्ते! Bonjour! こんにちは! مرحبا! 안녕하세요! Ciao! Cześć! Привіт! வணக்கம்!",
    ) -> Generator[bytearray] | AsyncGenerator[bytearray]:
    audio = self.client.generate(
      text=text, 
      voice=self.get_voice(voice_id), 
      model="eleven_multilingual_v2",
    )
    return audio 

if __name__=="__main__":
  def main():
    from .utils import collect_audio, save_bytes_to_mp3
    dialogue = ElevenSpeech()
    gen = dialogue.synthesize((dialogue.all_voices)[0].voice_id, "Hi David Sinclair, how have you been")
    audio = collect_audio(gen)
    save_bytes_to_mp3(audio, 'ficast-outputs/dialogue/test.mp3')
    play(audio)
    
  main()


