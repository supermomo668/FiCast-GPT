"use server";

import { MessageEntryUI } from "@/app/models/messages";
import { FiCastAPIResponse, PodcastRequestData } from "@/app/models/api_entry";
import { convertDialoguesToMessages } from "@/app/utils/messageConverter"; // Import the utility function
import { Participant } from "../models/participants";

const BACKEND_ACCESS_TOKEN = process.env.NEXT_PUBLIC_BACKEND_ACCESS_TOKEN;

export async function fetchPodcastScript({
  topic, n_rounds = 10, participants}: PodcastRequestData
  ): Promise<FiCastAPIResponse> {
  console.log("Sending podcast create request...");
  const requestBody: PodcastRequestData = {
    topic: topic,
    n_rounds: n_rounds, 
    participants: participants.map((speaker) => ({
      name: speaker.name,
      description: speaker.description,
      model: speaker.model,
      role: speaker.role,
    })),
  };
  const podcastCreateResponse = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/podcast/create`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.BACKEND_ACCESS_TOKEN}`,
      },
      body: JSON.stringify(requestBody),
    }
  );
  const data: FiCastAPIResponse = await podcastCreateResponse.json();
  return data;
}
// In backend_message.tsx

export async function getMessagesNewBackend(
  speakers: Participant[],
  n_rounds: number=10,
  topic: string,
  onMessageChanges: (messages: MessageEntryUI[]) => void
): Promise<MessageEntryUI[]> {
  const podcast_request: PodcastRequestData = {
    topic: topic,
    n_rounds: n_rounds,
    participants: speakers,
  }
  const data: FiCastAPIResponse = await fetchPodcastScript(podcast_request);
  console.log("getMessagesNewBackend: Data received from fetchPodcastScript:", data);

  const messages: MessageEntryUI[] = convertDialoguesToMessages(data.dialogues);
  console.log("getMessagesNewBackend: Converted messages:", messages);

  return messages;
}