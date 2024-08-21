import json, pathlib
from typing import Generator, AsyncGenerator, Union
import wave

from beartype import beartype

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

def save_bytes_to_wav(
    audio_bytes: bytes, save_path: pathlib.Path, n_channels=1, sampwidth=2, framerate=24000
    ):
    with wave.open(str(save_path), 'wb') as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        wf.writeframes(audio_bytes)
