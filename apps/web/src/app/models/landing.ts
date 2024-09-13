import { Dialogues } from "./podcast";
import {Participant, PodcastGroup} from "./participants"

export interface LandingProps {
  onStart: (data: {
     topic: string; 
     n_rounds: number;
     participants: Participant[] 
  }) => void;
}

export interface CharacterSelectorProps {
  onChange: (speakers: Set<string>) => void;
  selectedSpeakers: Set<string>;
  setSelectedSpeakers: React.Dispatch<React.SetStateAction<Set<string>>>;
  customName: string;
  setCustomName: React.Dispatch<React.SetStateAction<string>>;
  customDescription: string;
  setCustomDescription: React.Dispatch<React.SetStateAction<string>>;
}