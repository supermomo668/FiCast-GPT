from functools import lru_cache
from typing import Any, Dict, List, Generator, Union
from collections.abc import AsyncGenerator
import dotenv

from elevenlabs import Voice, play, voices

from .utils import CustomJSONEncoder
from .clients import tts_client_factory

dotenv.load_dotenv()

class TextToSpeech:
  def __init__(self, client_type: str, **kwargs: Any):
    """
    Initializes the TextToSpeech object.

    Args:
        client_type (str): The type of TTS client to use.
          Supported: 'api', 'elevenlabs'
    Returns:
        None
    """
    #### Init TTS Client
    self.client = tts_client_factory(client_type, **kwargs)

  @property
  def n_voices(self):
    return len(self.all_voices_by_id)

  @property
  @lru_cache(maxsize=None)
  def all_voices_by_id(self) -> Dict[str, Union[Voice, str, Any]]:
    return self.client.all_voices_by_id
  
  def get_voice(self, voice_id:str) -> Union[Voice, str]:
    """
    Retrieves a voice from the list of available voices based on the provided voice ID.
    Args:
        voice (str): The name of the voice to retrieve.
        save_meta (bool, optional): Whether to save the metadata of the retrieved voice. Defaults to True.
        output_dir (pathlib.Path, optional): The directory to save the metadata file. Defaults to "output/speech".
    Return: 
      The Voice object corresponding to the specified voice ID that `client.text_to_speech` identity with for generation
    """
    return self.all_voices_by_id[voice_id]

  def synthesize(
    self,
    text: str, voice_id: int, **kwargs
    ) -> Generator[bytearray, None, None] | AsyncGenerator[bytearray, None, None]:
    audio = self.client.text_to_speech(
      text=text, 
      voice=self.get_voice(voice_id),
      **kwargs
    )
    return audio 


if __name__=="__main__":
  def main():
    from .utils import collect_audio, save_bytes_to_mp3
    dialogue = TextToSpeech('elevenlabs')
    gen = dialogue.synthesize((dialogue.all_voices)[0].voice_id, "Hi David Sinclair, how have you been")
    audio = collect_audio(gen)
    save_bytes_to_mp3(audio, 'ficast-outputs/dialogue/test.mp3')
    play(audio)
    
  main()


