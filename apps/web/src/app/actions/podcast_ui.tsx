"use server";

import { Participant } from "@/app/models/particpants";
import { MessageType } from "@/app/models/messages";
import { Message } from "@/app/(components)/Message"; // Use Message from components
import { getMessagesNewBackend } from "./backend_message";
import { createStreamableUI } from "ai/rsc";

export async function getPodcast(
  topic: string,
  speakers: Participant[] // Accept an array of Participant objects
): Promise<JSX.Element | JSX.Element[] | null> {
  const weatherUI = createStreamableUI();
  weatherUI.update(<div>Loading podcast...</div>);

  const speakerNames = speakers.map((speaker) => speaker.name);

  try {
    const messages = await getMessagesNewBackend(
      speakerNames, topic, (msgList: MessageType[]) => {
      weatherUI.update(
        <div>
          {msgList.map((msg: MessageType) => (
            <Message 
              key={msg.id} 
              message={{
                name: msg.name,
                message: msg.message,
                thought: msg.thought
              }} 
            />
          ))}
        </div>
      );
    });

    weatherUI.done(
      <div>
        {messages.map((msg: MessageType) => (
          <Message 
            key={msg.id} 
            message={{
              name: msg.name,
              message: msg.message,
              thought: msg.thought
            }} 
          />
        ))}
      </div>
    );
  } catch (error) {
    console.error("Error fetching podcast messages:", error);
    weatherUI.done(
    <div className="text-red-500">Failed to load podcast messages.
    </div>
    );
  }

  return weatherUI.value!;
}