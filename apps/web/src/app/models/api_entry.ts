// Define the shape of the entry objects returned by the API
export interface ApiEntryType {
  message?: string;
  text?: string;
  speaker: string;
}

// Adjusted API response structure
export interface FiCastAPIResponse {
  title: string;
  abstract: string;
  dialogues: {
    speaker: {
      name: string;
      description: string;
    };
    dialogue: string;
    inner_thought: string;
  }[];
}