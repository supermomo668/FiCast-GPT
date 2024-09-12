export interface Character {
  name: string;
  image: string;
  description?: string;
  model?: string | null;
  role: "host" | "guest";
}

export interface Participant {
  name: string;
  description: string;
  // Model can be string or null
  model?: string | null; 
  role: string; // e.g., "guest" or "host"
}
