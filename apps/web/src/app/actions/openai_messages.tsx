"use server";

import { MessageType } from "@/app/models/messages";

import { generateObject, streamObject } from "ai";
import { z } from "zod";
import { openai } from "@ai-sdk/openai";

import { Pinecone } from "@pinecone-database/pinecone";
import OpenAI from "openai";

async function getMessagesOpenAI(
  speakers: [string, ...string[]],  // Ensure speakers is a tuple with at least one element
  topic: string,
  onMessageChanges: (messages: MessageType[]) => void
): Promise<MessageType[]> {
  const pc = new Pinecone({
    apiKey: process.env.PINECONE_API_KEY!,
  });
  const index = pc.Index("wikipedia-small");
  
  return new Promise(async (resolve) => {
    let done = false;
    // Initialize OpenAI and Pinecone clients with the API keys
    const openaiSdk = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY!,
    });
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