import { ReactNode } from "react";
import { Participant } from "./particpants";

export type PodcastProps = {
  topic: string;
  abstract?: string;
  speakers: string[];
  children: ReactNode;
  onClose?: () => void; // Add onClose as an optional prop
};


export interface PodcastData {
  topic: string;
  participants: Participant[];
}
