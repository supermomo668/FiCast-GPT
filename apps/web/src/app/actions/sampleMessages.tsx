"use server";

import { MessageEntryUI, MessageUI } from "../models/messages";
import { FiCastAPIResponse } from "../models/api_entry";


export async function getSampleMessagesBackend(
  speakers: string[],
  topic: string,
  onMessageChanges: (messages: MessageUI[]) => void
): Promise<MessageUI[]> {
  const search = new URLSearchParams();
  search.append("topic", topic);
  for (const speaker of speakers) {
    search.append("speakers", speaker);
  }

  const resp = await fetch(
    `${process.env.FICAST_URL}/samples/script`,
    {method: 'GET'},
  );

  if (!resp.ok) {
    throw new Error("Failed to get messages");
  }

  const data: FiCastAPIResponse = await resp.json(); // Adjust the type to match the backend response
  console.log("Data received:", data);
  // Mapping the dialogues to the required MessageUI structure
  const converted: MessageEntryUI[] = data.dialogues.map((entry) => ({
    id: Math.random().toString(32).substring(2), // unique ID
    name: entry.speaker.name, // speaker's name
    message: entry.dialogue.trim(), // the dialogue
    thought: entry.thought.trim()
  }));
  return converted;
}


// Optionally filter based on known characters
// const filtered = converted.filter((entry: MessageUI) => {
//   return LANDING_CHARACTERS.some((ch) => ch.name === entry.name);
// });

// return filtered;