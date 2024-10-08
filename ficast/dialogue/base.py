from typing import Any, Dict, List, Generator

from elevenlabs import Voice

class BaseTTSClient:
    def all_voices(self) -> List[Any]:
        raise NotImplementedError
    
    def all_voices_by_id(
        self, metadir: str = None, save_meta=False) -> Dict[str, Any]:
        raise NotImplementedError
                
    def text_to_speech(self, text: str, voice: str, **kwargs) -> Generator[bytearray, None, None]:
        raise NotImplementedError

    def get_queue_status(self):
        raise NotImplementedError

    def get_task_status(self, task_id: str):
        raise NotImplementedError
