import { ReactNode } from "react";
import { PodcastGroup } from "./participants";

import { Speaker } from "./participants";

interface PodcastBaseDefinition {
  topic: string;
  abstract?: string;
  participants: PodcastGroup;
}

// Podcast component props
export type PodcastProps = PodcastBaseDefinition & {
  children: ReactNode;
  onClose?: () => void; 
  // Add onClose as an optional prop
};

export interface PodcastUIProps extends PodcastBaseDefinition {
  messages: JSX.Element | JSX.Element[];
}

// Podcast data with Dialogues
export type Dialogues = {
  speaker: Speaker;
  dialogue: string;
  thought: string;
}[];

export interface PodcastData extends PodcastBaseDefinition {
  dialogues: Dialogues;
}