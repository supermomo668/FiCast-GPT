import { ReactNode } from "react";
import { Participant } from "./particpants";

export type Hosts = Participant[];
export type Guests = Participant[];
export type PodcastGroup = {
  hosts: Hosts;
  guests: Guests;
}

export type PodcastProps = {
  topic: string;
  abstract?: string;
  speakers: PodcastGroup;
  children: ReactNode;
  onClose?: () => void; // Add onClose as an optional prop
};

export interface PodcastData {
  topic: string;
  participants: PodcastGroup;
}
