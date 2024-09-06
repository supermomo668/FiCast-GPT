"use server";

import { Message } from "@/app/(components)/Message";
import { SAMPLE_MESSAGES } from "@/app/(components)/podcast";
import { createStreamableUI } from "ai/rsc";

import { generateObject, streamObject } from "ai";
import { z } from "zod";
import { openai } from "@ai-sdk/openai";
import { CharacterImages } from "@/app/(components)/CHARACTERS";

import { Pinecone } from "@pinecone-database/pinecone";
import OpenAI from "openai";

// Initialize OpenAI and Pinecone clients with the API keys
const openaiSdk = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
});

const pc = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY!,
});
const index = pc.Index("wikipedia-small");

// Define the shape of message objects returned by the backend
interface MessageType {
  id: string;
  message: string;
  name: string;
}

// Define the shape of the entry objects returned by the API
interface ApiEntryType {
  message?: string;
  text?: string;
  speaker: string;
}

async function getMessagesNewBackend(
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
    // `https://direct-lacewing-merry.ngrok-free.app/conversation?${search.toString()}`
    "http://104.197.25.48:42110/script"
  );
  
  if (!resp.ok) {
    throw new Error("Failed to get messages");
  }

  const messages: ApiEntryType[] = await resp.json();
  const converted = messages
    .map((entry: ApiEntryType) => {
      let message = entry.message || entry.text || "";
      if (message.startsWith("** ")) {
        message = message.replace("** ", "");
      }
      return {
        id: Math.random().toString(32).substring(2),
        message: message.trim(),
        name: entry.speaker,
      };
    })
    .filter((entry: MessageType) => {
      return CharacterImages.has(entry.name);
    });

  return converted;
}

async function getMessagesOpenAI(
  speakers: [string, ...string[]],  // Ensure speakers is a tuple with at least one element
  topic: string,
  onMessageChanges: (messages: MessageType[]) => void
): Promise<MessageType[]> {
  return new Promise(async (resolve) => {
    let done = false;

    const embedding = await openaiSdk.embeddings.create({
      model: "text-embedding-3-small",
      input: `${topic} — ${speakers.join(",")}`,
      encoding_format: "float",
    });

    const queryResponse = await index.query({
      vector: embedding.data[0].embedding,
      topK: 20,
      includeMetadata: true,
    });

    let knowledgeAddition = "";
    const knowledgeData = queryResponse.matches.map(
      (entry: any) => entry.metadata?.text || ""
    );
    knowledgeAddition = `
    You can use the following additional information: ${knowledgeData.join(
      "\n\n"
    )}
        `.trim();

    const { partialObjectStream } = await streamObject({
      onFinish: () => {
        done = true;
      },
      model: openai("gpt-4o"),
      schema: z.object({
        messages: z.array(
          z.object({
            id: z.string().uuid(),
            name: z.enum(speakers as [string, ...string[]]),  // Cast to a tuple
            message: z.string(),
          })
        ),
      }),
      prompt: `
Generate a dialog of 40 messages between the following parties ${speakers.join(
        ", "
      )}. The topic is ${topic}.${knowledgeAddition}`.trim(),
    });

    for await (const partialObject of partialObjectStream) {
      if (done && partialObject.messages) {
        resolve(partialObject.messages);
      } else if (partialObject.messages) {
        onMessageChanges(partialObject.messages);
      }
    }
  });
}



export async function getPodcast(
  topic: string,
  speakers: [string, ...string[]],
  // useOpenai: boolean
): Promise<JSX.Element> {
  const weatherUI = createStreamableUI();

  weatherUI.update(<>...</>);

  // const getMessages = useOpenai ? getMessagesOpenAI : getMessagesNewBackend;
  const getMessages = getMessagesNewBackend;
  getMessages(speakers, topic, (messages) => {
    if (Array.isArray(messages))
      weatherUI.update(
        <>
          {
            messages.map((msg: MessageType) => (
              <Message message={msg} key={msg.id} />
            ))
          }
        </>
      );
  }).then((messages) => {
    weatherUI.done(
      <>
        {
          messages.map((msg: MessageType) => (
            <Message message={msg} key={msg.id} />
          ))
        }
      </>
    );
  });

  return weatherUI.value;
}
