from functools import lru_cache
from pathlib import Path
import warnings
import tqdm
import hydra
from omegaconf import DictConfig, OmegaConf
from hydra import initialize, compose

from typing import Any, TypeVar, List, Union
from pydantic import Field

from ficast.assembly.base import ConvCast
from ficast.conversation.base import Conversation
from ficast.dialogue.synthesis import DialogueSynthesis 
from ficast.conversation.podcast import Podcast
from ficast.dialogue.utils import save_bytes_to_mp3

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
    dialogue_synthesizer: DialogueSynthesis = Field(default_factory=lambda: DialogueSynthesis())
    synthesized_audio: Union[str, bytes] = None
    audio_encoding: str = "latin-1"
    model_config = {
        "arbitrary_types_allowed": True
    }
    def __init__(
        self, 
        conversation: "Podcast", **kwargs: Any
        ):
        super().__init__(conversation=conversation, **kwargs)

    def inject_music(self, style: str = "auto") -> None:
        """Inject music into the podcast."""
        # TODO: Implement music injection based on style
        raise NotImplementedError("Please implement inject_music()")
    
    @lru_cache(maxsize=None)
    def to_podcast(self, include_inner_thoughts: bool = False, use_json_script: bool = True) -> str:
        """
        Convert the conversation to an audio podcast.

        Args:
            include_inner_thoughts (bool, optional): Whether to include inner thoughts in the podcast. Defaults to False.
            use_json_script (bool, optional): Whether to use the JSON script to generate the podcast. Defaults to True.

        Returns:
            str: The synthesized audio content of the podcast.

        """
        audio_segments = []
        voice_mapping = {}
        scipt_src = self.conversation.json_script.get("dialogues") if use_json_script else self.conversation.script
        # Map each participant to a unique voice based on their gender
        for participant in self.conversation.participants:
            gender = participant.gender.lower()
            if gender not in ['male', 'female']:
                gender = 'andy'  # Default to 'andy'
            nth = len([p for p in self.conversation.participants if p.gender.lower() == gender])
            voice_mapping[participant.name] = self.dialogue_synthesizer.get_nth_voice_by_gender(nth - 1, gender)

        # Iterate through the json_script to process each dialogue
        for entry in tqdm.tqdm(scipt_src, desc="Processing script entries"):
            speaker_name = entry["speaker"]["name"]
            # Get the voice for the speaker
            if speaker_name in voice_mapping:
                # Synthesize the dialogue text
                for audio_chunk in self.dialogue_synthesizer.synthesize(
                    voice_mapping[speaker_name].voice_id,  entry.get("dialogue")):
                    audio_segments.append(audio_chunk)
                    
                # Optionally synthesize inner thoughts if needed
                if include_inner_thoughts:
                    for audio_chunk in self.dialogue_synthesizer.synthesize(
                        voice_mapping[speaker_name].voice_id, entry.get("inner_thoughts")):
                        audio_segments.append(audio_chunk)
            else:
                warnings.warn(f"No voice found for speaker {speaker_name}")

        # Combine all audio segments into a single podcast audio stream
        self.synthesized_audio = self.combine_audio_segments(audio_segments)
        # Return the combined audio as the podcast content
        return self.synthesized_audio

    def combine_audio_segments(self, audio_segments: List[bytearray]) -> str:
        """Combine all audio segments into a single audio stream."""
        # Placeholder implementation for combining audio segments
        # In a real implementation, you would use an audio processing library to combine bytearrays
        combined_audio = b''.join(audio_segments)
        return combined_audio.decode(self.audio_encoding)  # Convert bytearray to string for representation
    
    def save_podcast(self, path: str) -> None:
        """
        Save the podcast to the specified path.
        Args:
            path (str): The path to save the podcast.
        """
        if hasattr(self, 'synthesized_audio'):
           # Save the podcast to the specified path
            save_bytes_to_mp3(self.synthesized_audio.encode(self.audio_encoding), path)
        else:
            raise RuntimeError("No podcast content attribute `synthesized_audio` to save. Please run `.to_podcast()` first to syntehsise the podcast.")
        
    
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
    main()