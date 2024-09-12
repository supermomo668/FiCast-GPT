"use server";

import { MessageType } from "@/app/models/messages";
import { FiCastAPIResponse } from "@/app/models/api_entry";
import { LANDING_CHARACTERS } from "@/app/(components)/CHARACTERS";

// Define the server-side access token (retrieved from environment variables)
const BACKEND_ACCESS_TOKEN = process.env.NEXT_PUBLIC_BACKEND_ACCESS_TOKEN;

export async function getMessagesNewBackend(
  speakers: string[],
  topic: string,
  onMessageChanges: (messages: MessageType[]) => void
): Promise<MessageType[]> {
  // Create the podcast with a POST request
  console.log("Sending podcast create request...");
  const podcastCreateResponse = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/podcast/create`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${BACKEND_ACCESS_TOKEN}`,
      },
      body: JSON.stringify({
        topic: topic,
        n_rounds: 10, // Number of rounds
        participants: speakers.map((speaker) => ({
          name: speaker,
          description: LANDING_CHARACTERS.find((ch) => ch.name === speaker)?.description || "",
          model: process.env.NEXT_PUBLIC_DEFAULT_MODEL,
          role: LANDING_CHARACTERS.find((ch) => ch.name === speaker)?.role || null,
        })),
      }),
    }
  );

  if (!podcastCreateResponse.ok) {
    throw new Error("Failed to create podcast");
  }

  const { task_id } = await podcastCreateResponse.json();
  console.log(`Retrieving podcast ID ${task_id}`);
  // Retrieve the script using the task ID
  const scriptResponse = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/podcast/${task_id}/script`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${BACKEND_ACCESS_TOKEN}`,
      },
    }
  );
  console.log("Script Response:", scriptResponse);
  if (!scriptResponse.ok) {
    throw new Error("Failed to retrieve script");
  }

  const data: FiCastAPIResponse = await scriptResponse.json();

  // Mapping the dialogues to the required MessageType structure
  const converted: MessageType[] = data.dialogues.map((entry) => ({
    id: Math.random().toString(32).substring(2), // random unique ID
    name: entry.speaker.name, // Use the speaker's name
    message: entry.dialogue.trim(), // Extract and trim the dialogue
    thought: entry.inner_thought.trim()
  }));
  return converted;
  // Optionally filter based on known characters
  // const filtered = converted.filter((entry: MessageType) => {
  //   return LANDING_CHARACTERS.some((ch) => ch.name === entry.name);
  // });

  // return filtered;
}
