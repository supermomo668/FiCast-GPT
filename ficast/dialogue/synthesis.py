from typing import Dict, List
import warnings
import dotenv
from elevenlabs import play, stream, save

from .speech import ElevenSpeech

dotenv.load_dotenv()

  
class DialogueSynthesis(ElevenSpeech):
  audio_encoding: str = "latin-1"
  def __init__(self):
    super().__init__()
    
  def get_nth_voice_by_gender(self, nth: int, gender: str):
    assert gender in ['male', 'female', 'andy'], "Not a supported gender"
    nth_voice = 0
    for voice in self.all_voices:
      if voice.labels["gender"] == gender:
        gender_voice = voice
        if nth == nth_voice:
          return gender_voice
        nth_voice += 1
    warnings.warn(f"Could not find the {nth} voice for gender {gender}. Using the (n_available % nth) voice which is the {nth_voice} voice. Check as it may not be the desired or duplicate with existing voices")
    return self.get_nth_voice_by_gender(nth % nth_voice, gender)

  
if __name__=="__main__":
  from .utils import collect_audio, save_bytes_to_mp3
  def main():
    dialogue = DialogueSynthesis()
    gen = dialogue.synthesize(
      (dialogue.all_voices)[0].voice_id, 
      "Hi David, how have you been?"
    )
    audio = collect_audio(gen)
    save_bytes_to_mp3(audio, 'ficast-outputs/dialogue/test.mp3')
    play(audio)
    
  main()