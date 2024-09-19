"use server"

import { createStreamableUI } from "ai/rsc"; // Keep weatherUI

import { createPodcastScript } from './backend_message';
import { fetchStatus } from './task_status';
import { MessageDisplay } from '@/app/(components)/Message';
import { PodcastRequestData, FiCastAPIResponse, TaskStatusResponse } from '@/app/models/api_entry';
import { convertDialoguesToMessages } from "../utils/messageConverter";

import { FicastAPIClient } from '@/lib/ficast_client';

export async function getPodcast(data: PodcastRequestData): Promise<{ ui: JSX.Element | JSX.Element[] | null, error?: string }> {
  if (typeof window === 'undefined') {
    throw new Error('getPodcast should be run on the client side.');
  }

  const weatherUI = createStreamableUI();
  weatherUI.update(<div>Starting podcast creation...</div>);

  try {
    // Step 1: Create podcast script and get task ID
    const { task_id } = await createPodcastScript(data);

    // Step 2: Wait for task completion on the client-side
    const finalStatus = await fetchStatus(task_id);

    if (!finalStatus || finalStatus.script_status?.toLowerCase() !== 'script_created') {
      return { ui: null, error: 'Podcast script generation failed or was incomplete.' };
    }

    const podcastScriptResponse = await FicastAPIClient.get<FiCastAPIResponse>(`/podcast/${task_id}/script`);
    const podcast = podcastScriptResponse.data;

    const messages = convertDialoguesToMessages(podcast.dialogues);

    weatherUI.update(<MessageDisplay messages={messages} />);
    weatherUI.done();

    return { ui: weatherUI.value as JSX.Element, error: undefined };
  } catch (error: any) {
    console.error("Error fetching podcast:", error);
    weatherUI.update(<div className="text-red-500">Failed to load podcast messages: {error.message}</div>);
    weatherUI.done();
    return { ui: null, error: `Failed to load podcast messages: ${error.message}` };
  }
}


