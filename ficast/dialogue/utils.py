import json
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def collect_audio(audio_generator: generator[bytearray] | AsyncGenerator[bytearray]):
    audio_data = bytearray()
    for chunk in audio_generator:
      audio_data.extend(chunk)
    return audio_data
  
def save_bytes_to_mp3(byte_data, file_name=pathlib.Path('ficast-outputs/dialogue/test.mp3')):
  pathlib.Path(file_name).parent.mkdir(parents=True, exist_ok=True)
  with open(file_name, 'wb') as file:
    file.write(byte_data)
  