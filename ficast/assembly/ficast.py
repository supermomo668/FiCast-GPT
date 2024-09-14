from datetime import datetime
from functools import lru_cache
import io
from pathlib import Path
import warnings
from beartype import beartype
import tqdm
import hydra
from omegaconf import DictConfig, OmegaConf

from typing import Any, TypeVar, List, Union
from pydantic import Field

from ficast.assembly.base import ConvCast
from ficast.conversation.base import Conversation
from ficast.dialogue.speech import DialogueSynthesis 
from ficast.conversation.podcast import Podcast
from ficast.dialogue.utils import save_bytes_to_wav

from ..character.utils import get_all_participants, update_existing_character
class FiCast(ConvCast):
    """
    A class to assemble and create a podcast conversation.

    Attributes:
    -----------
    config : Any
        Configuration for the podcast.
    conversation : Conversation
        Conversation object with details of the podcast.

    Methods:
    --------
    inject_music(style: str) -> 'FiCast':
        Injects music into the podcast.
    to_podcast() -> str:
        Converts the conversation to an audio podcast.
    """
    conversation: Podcast = TypeVar("conversation", bound=Conversation)
    dialogue_synthesizer: DialogueSynthesis = Field(
        default_factory=lambda: DialogueSynthesis())
    audio_segments: List[bytes] = Field(default_factory=list)
    frame_rate: int = 24000
    model_config = {
        "arbitrary_types_allowed": True
    }
    def __init__(
        self, 
        conversation: Podcast, **kwargs: Any
        ):
        super().__init__(conversation=conversation, **kwargs)

    def inject_music(self, style: str = "auto") -> None:
        """Inject music into the podcast."""
        # TODO: Implement music injection based on style
        raise NotImplementedError("Please implement inject_music()")
    
    def _update_participants_sex_from_script(self, json_script: dict) -> None:
        if "participants" in json_script:
            json_participants = get_all_participants(json_script['participants'])
            return update_existing_character(
                self.conversation.participants, json_participants)
        else:
            return False

    @lru_cache(maxsize=None)
    def to_podcast(
        self, include_inner_thoughts: bool = False, use_json_script: bool = True,
        **tts_kwargs: Any
        ) -> str:
        """
        Convert the conversation to an audio podcast.

        Args:
            include_inner_thoughts (bool, optional): Whether to include inner thoughts in the podcast. Defaults to False.
            use_json_script (bool, optional): Whether to use the JSON script to generate the podcast. Defaults to True.

        Returns:
            str: The synthesized audio content of the podcast.

        """
        self.audio_segments = []
        voice_mapping = {}
        scipt_src = self.conversation.json_script.get("dialogues") if use_json_script else self.conversation.script
        # use script to populate characters sex if not specified
        self.conversation.participants = self._update_participants_sex_from_script(json_script=self.conversation.json_script)
        # Map each participant to a unique voice based on their gender
        for participant in self.conversation.participants:
            nth = len([p for p in self.conversation.participants if p.sex.lower() == participant.sex.lower()])
            voice_mapping[participant.name] = self.dialogue_synthesizer.get_nth_voice_by_gender(nth - 1, participant.sex.lower())
          
        # Iterate through the json_script to process each dialogue
        for entry in tqdm.tqdm(scipt_src, desc="Processing script entries"):
            speaker_name = entry["speaker"]["name"]
            # Get the voice for the speaker
            if speaker_name in voice_mapping:
                # Synthesize the dialogue text
                for audio_chunk in self.dialogue_synthesizer.synthesize(
                    entry.get("dialogue"),
                    voice_mapping[speaker_name].voice_id,
                    **tts_kwargs
                    ):
                    self.audio_segments.append(audio_chunk)
                    
                # Optionally synthesize inner thoughts if needed
                if include_inner_thoughts:
                    for audio_chunk in self.dialogue_synthesizer.synthesize(
                        voice_mapping[speaker_name].voice_id, entry.get("inner_thoughts")):
                        self.audio_segments.append(audio_chunk)
            else:
                raise ValueError(f"Speaker {speaker_name} not found in voice mapping.")

        # Combine all audio segments into a single podcast audio stream
        print(f"Joined {len(self.audio_segments)} audio segments")
        return b''.join(self.audio_segments)
    
    def save_podcast(
        self, save_path: str, save_segments: bool = False) -> None:
        """
        Save the podcast to the specified path.
        Args:
            path (str): The directory to save the podcast.
        """
        save_path = Path(save_path)
        save_path = save_path/f"my_podcast-{datetime.now().strftime('%Y%m%d_%H%M')}"
        if save_segments:
            save_path.mkdir(parents=True, exist_ok=True)
        
        if hasattr(self, 'audio_segments'):        
            # Save the full podcast as a WAV file
            save_bytes_to_wav(
                b"".join(self.audio_segments), save_path/"podcast.wav", framerate=self.frame_rate)

        if save_segments:
            for i, audio_chunk in enumerate(self.audio_segments):
                save_bytes_to_wav(audio_chunk, save_path/f"{i}.wav", framerate=self.frame_rate)
            print(f"Content saved to {save_path}")
        else:
            raise RuntimeError("No podcast content attribute `synthesized_audio` to save. Please run `.to_podcast()` first to synthesize the podcast.")

    def __hash__(self):
        # Define a hash function based on the fields that uniquely identify the object
        return hash((self.conversation,))

    def __eq__(self, other):
        # Define equality based on the fields that uniquely identify the object
        if isinstance(other, FiCast):
            return self.conversation == other.conversation
        return False
    
__all__ = ["FiCast"]


@hydra.main(version_base=None, config_path="../../conf/dialogue", config_name="default")
def main(cfg: DictConfig) -> None:
    # Convert the OmegaConf config to the Pydantic model
    config_dict = OmegaConf.to_container(cfg, resolve=True)


if __name__ == "__main__":
    from hydra import initialize, compose
    main()