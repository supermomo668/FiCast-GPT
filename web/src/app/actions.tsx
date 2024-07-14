"use server";

import { Message } from "@/components/Message";
import { SAMPLE_MESSAGES } from "@/components/podcast";
import { createStreamableUI } from "ai/rsc";

import { generateObject, streamObject } from "ai";
import { z } from "zod";
import { openai } from "@ai-sdk/openai";
import { CharacterImages } from "@/components/CHARACTERS";

import { Pinecone } from "@pinecone-database/pinecone";
import OpenAI from "openai";

const openaiSdk = new OpenAI();

const pc = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY!,
});
const index = pc.Index("wikipedia-small");

async function getMessagesNewBackend(
  speakers: string[],
  topic: string,
  onMessageChanges: any
) {
  const search = new URLSearchParams();
  search.append("topic", topic);
  for (const speaker of speakers) {
    search.append("speakers", speaker);
  }
  const resp = await fetch(
    `https://direct-lacewing-merry.ngrok-free.app/conversation?${search.toString()}`
  );
  console.log(resp.url);
  if (!resp.ok) {
    throw new Error("Failed to get messages");
  }
  const messages = await resp.json();
  const converted = messages
    .map((entry) => {
      let message = entry.message || entry.text;
      if (message.startsWith("** ")) {
        message = message.replace("** ", "");
      }
      return {
        id: Math.random().toString(32).substring(2),
        message: message.trim(),
        name: entry.speaker,
      };
    })
    .filter((entry) => {
      return CharacterImages.has(entry.name);
    });

  return converted;
}

function getMessagesOpenAI(speakers, topic, onMessageChanges) {
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
      (entry) => entry.metadata?.text || ""
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
            name: z.enum(speakers),
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
      if (done) {
        resolve(partialObject.messages);
      } else {
        onMessageChanges(partialObject.messages);
      }
    }
  });
}

export async function getPodcast(
  topic: string,
  speakers: [string, ...string[]],
  useOpenai: boolean
) {
  const weatherUI = createStreamableUI();

  weatherUI.update(<>...</>);

  const getMessages = useOpenai ? getMessagesOpenAI : getMessagesNewBackend;

  getMessages(speakers, topic, (messages) => {
    if (Array.isArray(messages))
      weatherUI.update(
        <>
          {
            // @ts-ignore
            messages.map((msg) => (
              <Message message={msg} key={msg.id} />
            ))
          }
        </>
      );
  }).then((messages) => {
    weatherUI.done(
      <>
        {
          // @ts-ignore
          messages.map((msg) => (
            <Message message={msg} key={msg.id} />
          ))
        }
      </>
    );
  });

  return weatherUI.value;
}
