"use server";

import { MessageType } from "./models/messages";
import { ApiEntryType, FiCastAPIResponse } from "./models/api_entry";
import { LANDING_CHARACTERS } from "@/app/(components)/CHARACTERS";
import { Message } from "@/app/(components)/Message";

import { ReactElement } from "react"; // Import ReactElement for type consistency

import { createStreamableUI } from "ai/rsc";


export async function getMessagesNewBackend(
  speakers: string[],
  topic: string,
  onMessageChanges: (messages: MessageType[]) => void
): Promise<MessageType[]> {
  const search = new URLSearchParams();
  search.append("topic", topic);
  for (const speaker of speakers) {
    search.append("speakers", speaker);
  }

  const resp = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/samples/script`,
    {method: 'GET'},
  );

  if (!resp.ok) {
    throw new Error("Failed to get messages");
  }

  const data: FiCastAPIResponse = await resp.json(); // Adjust the type to match the backend response
  console.log("Data received:", data);
  // Mapping the dialogues to the required MessageType structure
  const converted: MessageType[] = data.dialogues.map((entry) => ({
    id: Math.random().toString(32).substring(2), // Generate a random unique ID
    message: entry.dialogue.trim(), // Extract and trim the dialogue
    name: entry.speaker.name, // Use the speaker's name
  }));

  // Optionally filter based on known characters
  const filtered = converted.filter((entry: MessageType) => {
    return LANDING_CHARACTERS.some((ch) => ch.name === entry.name);
  });

  return filtered;
}

