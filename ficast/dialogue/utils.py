import json, pathlib
from typing import Generator, AsyncGenerator, Union
import wave, ffmpeg, struct

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
    audio_bytes: bytes, save_path: pathlib.Path, n_channels=2, sampwidth=2, framerate=24000
):
    # Determine the number of float32 samples
    num_samples = len(audio_bytes) // 4  # 4 bytes per float32 sample

    # Unpack the bytes to get float samples
    float_samples = struct.unpack('<' + 'f' * num_samples, audio_bytes)

    # Convert float samples to int16 samples
    int_samples = []
    for sample in float_samples:
        # Clip the sample to the range -1.0 to 1.0
        sample = max(min(sample, 1.0), -1.0)
        # Scale the sample to int16 range
        int_sample = int(sample * 32767)
        int_samples.append(int_sample)

    # Handle stereo channels by interleaving samples
    if n_channels == 2:
        stereo_samples = []
        for int_sample in int_samples:
            # Duplicate sample for left and right channels
            stereo_samples.extend([int_sample, int_sample])
        int_samples = stereo_samples

    # Pack int16 samples into bytes
    audio_int16_bytes = struct.pack('<' + 'h' * len(int_samples), *int_samples)

    with wave.open(str(save_path), 'wb') as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        wf.writeframes(audio_int16_bytes)

def convert_wav_to_mp3(input_file: str, output_file: str):
    try:
        # Convert the WAV file to MP3 format
        ffmpeg.input(input_file).output(output_file).run()
        print(f"Successfully converted {input_file} to {output_file}")
    except Exception as e:
        print(f"Error converting file: {e}")