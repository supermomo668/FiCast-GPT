from typing import Dict, List
import dotenv

from .speech import ElevenSpeech

dotenv.load_dotenv()

  
class DialogueSynthesis(ElevenSpeech):
  def __init__(self):
    super().__init__()
    
  def chat_to_speech(self, chat: List[Dict]):
    pass
  
if __name__=="__main__":
  from .utils import collect_audio, save_bytes_to_mp3
  def main():
    dialogue = DialogueSynthesis()
    gen = dialogue.synthesize((dialogue.all_voices)[0].voice_id, "Hi David Sinclair, how have you been")
    audio = collect_audio(gen)
    save_bytes_to_mp3(audio, 'ficast-outputs/dialogue/test.mp3')
    play(audio)
    
  main()
