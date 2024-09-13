import { Participant } from "./participants";
import { Dialogues } from "./podcast";

// Define the shape of the entry objects returned by the API
export interface ApiEntryType {
  message?: string;
  text?: string;
  speaker: string;
}

export interface PodcastRequestData{
  topic: string;
  n_rounds? : number;
  participants: Participant[];
}
// Adjusted API response structure
export interface FiCastAPIResponse {
  title: string;
  abstract: string;
  dialogues: Dialogues;
}