from elevenlabs import generate, play, voices, VoiceSettings, Voice
import requests, yaml, random

voices = voices()
def _get_random_voice_settings():
  # as suggested by limits of ElevenLab. Greatly impacted by voice
  return VoiceSettings(
    stability=random.uniform(0.3, 1), 
    similarity_boost=random.random(),
    style=random.random(),
    use_speaker_boost=True
  )

def _get_random_voice():
  return random.choice(voices)

def random_synthesize(
  text="Hello! 你好! Hola! नमस्ते! Bonjour! こんにちは! مرحبا! 안녕하세요! Ciao! Cześć! Привіт! வணக்கம்!"
  ):
  audio = generate(
    text=text, 
    voice=_get_random_voice(), 
    model="eleven_multilingual_v2",
    settings=_get_random_voice_settings()
  )
  return audio 

def save_bytes_to_mp3(byte_data, file_name):
    with open(file_name, 'wb') as file:
        file.write(byte_data)


if __name__=="__main__":
  audio=random_synthesize()
  save_bytes_to_mp3(audio, 'test')
  print("\nGenerated Audio:\n", len(audio))
  play(audio)