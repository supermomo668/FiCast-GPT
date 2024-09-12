"use server";

import { ReactElement } from "react";
import type { JSXElementConstructor } from 'react';

import { Participant } from "@/app/models/particpants";
import { MessageType } from "@/app/models/messages";
import { getMessagesNewBackend } from "./backend_message";
import { createStreamableUI } from "ai/rsc";
import { MessageDisplay } from "@/app/(components)/Message"; // Import MessageDisplay
import { PodcastGroup } from "../models/podcast";

export async function getPodcast(
  topic: string,
  speakers: PodcastGroup // Accept an array of Participant objects
): Promise<JSX.Element | JSX.Element[] | null> {
  const weatherUI = createStreamableUI();
  weatherUI.update(<div>Loading podcast...</div>);

  const speakerNames = speakers.map((speaker) => speaker.name);

  try {
    const messages = await getMessagesNewBackend(
      speakerNames, topic, (msgList: MessageType[]) => {
      weatherUI.update(<MessageDisplay messages={msgList} />);
    });

    weatherUI.done(<MessageDisplay messages={messages} />);
  } catch (error) {
    console.error("Error fetching podcast messages:", error);
    weatherUI.done(<div className="text-red-500">Failed to load podcast messages.</div>);
  }
  // Return null if the value is undefined or null
  if (weatherUI.value === undefined || weatherUI.value === null) {
    return null;
  } else if (Array.isArray(weatherUI.value) && weatherUI.value.every((item) => item instanceof Element)
  ) {
    return weatherUI.value;
  } else if (weatherUI.value instanceof Element) {
    return weatherUI.value as ReactElement<any, string | JSXElementConstructor<any>> | ReactElement<any, string | JSXElementConstructor<any>>[];
  } else {
    throw new Error('Invalid value type');
  }
}