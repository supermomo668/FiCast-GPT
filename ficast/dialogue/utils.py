import json, pathlib
from typing import Generator, AsyncGenerator

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def collect_audio(audio_generator: Generator[bytearray, None, None] | AsyncGenerator[bytearray, None]):
    """
    Collects audio data from a generator or asynchronous generator.
    Returns:
        bytearray: The collected audio data.
    """
    audio_data = bytearray()
    for chunk in audio_generator:
      audio_data.extend(chunk)
    return audio_data


def save_bytes_to_mp3(
  byte_data: bytearray, file_name=pathlib.Path('ficast-outputs/dialogue/test.mp3')):
  """
  Saves the given byte data as an MP3 file at the specified file path.
  Returns:
    None
  """
  pathlib.Path(file_name).parent.mkdir(parents=True, exist_ok=True)
  with open(file_name, 'wb') as file:
    file.write(byte_data)
  