export interface Speaker {
  name: string;
  description?: string | null;
  sex?: string | null;
}

export interface Character extends Speaker {
  image: string;
  model?: string | null;
  role: "host" | "guest";
}

export interface Participant extends Speaker {
  model?: string | null; 
  role?: string | null; // e.g., "guest" or "host"
}

export type Hosts = Participant[];
export type Guests = Participant[];
export type PodcastGroup = {
  hosts: Hosts;
  guests: Guests;
}