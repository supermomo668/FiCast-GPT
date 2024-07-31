import warnings
import hydra
from omegaconf import DictConfig, OmegaConf
from hydra import initialize, compose
from typing import Any, TypeVar, List

from ficast.assembly.base import ConvCast
from ficast.conversation.base import Conversation
from ficast.dialogue.synthesis import DialogueSynthesis 
from ficast.conversation.podcast import Podcast

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
    dialogue_synth: DialogueSynthesis = DialogueSynthesis()

    def __init__(
        self, 
        conversation: Podcast, **kwargs: Any
        ):
        super().__init__(conversation=conversation, **kwargs)
        self.conversation = conversation

    def inject_music(self, style: str = "auto") -> None:
        """Inject music into the podcast."""
        # TODO: Implement music injection based on style
        print(f"Injecting {style} music into the podcast.")

    def script_to_podcast(self) -> str:
        """Convert the conversation to an audio podcast."""
        audio_segments = []
        voice_mapping = {}

        # Map each participant to a unique voice based on their gender
        for participant in self.conversation.participants:
            gender = participant.sex.lower()
            if gender not in ['male', 'female']:
                gender = 'andy'  # Default to 'andy' if gender is not male or female
            nth = len([p for p in self.conversation.participants if p.gender.lower() == gender])
            voice_mapping[participant.name] = self.dialogue.get_nth_voice_by_gender(nth - 1, gender)

        # Iterate through the json_script to process each dialogue
        for entry in self.conversation.json_script:
            dialogue_text = entry.get('dialogue', '')
            inner_thought_text = entry.get('inner_thought', '')
            speaker_name = entry.get('speaker', '')
            # Get the voice for the speaker
            if speaker_name in voice_mapping:
                voice = voice_mapping[speaker_name]
                voice_id = voice.voice_id

                # Synthesize the dialogue text
                for audio_chunk in self.dialogue.synthesize(voice_id, dialogue_text):
                    audio_segments.append(audio_chunk)

                # Optionally synthesize inner thoughts if needed
                if inner_thought_text:
                    for audio_chunk in self.dialogue.synthesize(voice_id, inner_thought_text):
                        audio_segments.append(audio_chunk)
            else:
                warnings.warn(f"No voice found for speaker {speaker_name}")

        # Combine all audio segments into a single podcast audio stream
        combined_audio = self.combine_audio_segments(audio_segments)

        # Return the combined audio as the podcast content
        return combined_audio

    def combine_audio_segments(self, audio_segments: List[bytearray]) -> str:
        """Combine all audio segments into a single audio stream."""
        # Placeholder implementation for combining audio segments
        # In a real implementation, you would use an audio processing library to combine bytearrays
        combined_audio = b''.join(audio_segments)
        return combined_audio.decode('latin1')  # Convert bytearray to string for representation

@hydra.main(version_base=None, config_path="../../conf/dialogue", config_name="default")
def main(cfg: DictConfig) -> None:
    # Convert the OmegaConf config to the Pydantic model
    config_dict = OmegaConf.to_container(cfg, resolve=True)


if __name__ == "__main__":
    main()
