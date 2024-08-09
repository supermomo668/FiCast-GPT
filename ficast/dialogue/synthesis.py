import random
from typing import Dict, List
import warnings
import dotenv
from elevenlabs import play, stream, save

from .speech import TextToSpeech

dotenv.load_dotenv()

  
class DialogueSynthesis(TextToSpeech):
  audio_encoding: str = "latin-1"
  def __init__(self, client_type="elevenlabs", **kwargs):
    super().__init__(client_type=client_type, **kwargs)
    
  def get_random_voices(self):
    voices = list(self.all_voices_by_id.values())
    random.shuffle(voices)
    return voices
  
  def get_random_voice(self):
    return self.get_random_voices()[0]
    
  def get_nth_voice_by_gender(self, nth: int, gender: str=None):
    if gender is None:
      return self.get_random_voice()
    assert gender in ['male', 'female', 'andy'], "Not a supported gender, must be 'male', 'female' or 'andy'"
    # loop through voices
    nth_voice = 0
    for _, voice in self.all_voices_by_id.items():
      if voice.labels.get("gender") == gender:
        gender_voice = voice
        if nth == nth_voice:
          return gender_voice
        nth_voice += 1
    if nth_voice == 0 or nth > nth_voice:
      warnings.warn(f"Could not find the {nth} voice for gender {gender}. Using the (n_available % nth) voice which is the {nth_voice} voice. Check as it may not be the desired or duplicate with existing voices", UserWarning)
    return self.get_random_voice()

  
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