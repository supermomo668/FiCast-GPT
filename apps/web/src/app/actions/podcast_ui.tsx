"use server";

import { ReactElement } from "react";
import { MessageEntryUI } from "@/app/models/messages";
import { fetchPodcastScript, getMessagesNewBackend } from "./backend_message";
import { createStreamableUI } from "ai/rsc";
import { MessageDisplay } from "@/app/(components)/Message"; // Import MessageDisplay
import { Participant } from "../models/participants";
import { convertDialoguesToMessages } from "../utils/messageConverter";
import { FiCastAPIResponse, PodcastRequestData } from "../models/api_entry";

export async function getPodcast({
  topic,
  n_rounds,
  participants
}: PodcastRequestData): Promise<JSX.Element | JSX.Element[] | null> {
  
  const weatherUI = createStreamableUI();
  weatherUI.update(<div>Loading podcast...</div>);
  const podcast_request: PodcastRequestData = {
    topic: topic,
    n_rounds: n_rounds,
    participants: participants,
  }
  try {
    const podcast: FiCastAPIResponse = await fetchPodcastScript(podcast_request);
    const messages: MessageEntryUI[] = convertDialoguesToMessages(podcast.dialogues);
    // const messages = await getMessagesNewBackend(participants, topic, (msgList: MessageEntryUI[]) => {
    //   weatherUI.update(<MessageDisplay messages={msgList} />);
    // });
    weatherUI.update(<MessageDisplay messages={messages} />);
    // weatherUI.done(<MessageDisplay messages={messages} />);
  } catch (error) {
    console.error("Error fetching podcast messages:", error);
    weatherUI.done(<div className="text-red-500">Failed to load podcast messages.</div>);
  }

  const value = weatherUI.value;
  if (!value || typeof value === "undefined") {
    return null;
  }

  if (Array.isArray(value) || (value as ReactElement)?.type) {
    return value as JSX.Element | JSX.Element[];
  }
  return weatherUI.value as JSX.Element;
}
