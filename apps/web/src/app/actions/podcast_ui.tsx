"use server"

import { createPodcastScript, waitTaskComplete } from './backend_message';
import { MessageDisplay } from '@/app/(components)/Message';
import { PodcastRequestData, FiCastAPIResponse, TaskStatusResponse } from '@/app/models/api_entry';
import { convertDialoguesToMessages } from "../utils/messageConverter";

import { FicastAPIClient } from '@/lib/ficast_client';
import { createStreamableUI } from "ai/rsc"; // Keep weatherUI

export async function getPodcast(data: PodcastRequestData): Promise<{ ui: JSX.Element | JSX.Element[] | null, error?: string } | undefined > {
  const weatherUI = createStreamableUI(); // Initialize weatherUI
  weatherUI.update(<div>Starting podcast creation...</div>);

  try {
    // Step 1: Create Podcast Task and get task_id
    const { task_id } = await createPodcastScript(data);

    // Step 2: Poll task status until script is created
    const finalStatus = await waitTaskComplete(task_id);

    // Step 3: Handle if the task failed
    if (finalStatus.script_status.toLowerCase() === 'failure') {
      return { ui: null, error: 'Failed to generate the podcast script.' };
    }

    // Step 4: Fetch the final script once the status is SCRIPT_CREATED
    const podcastScriptResponse = await FicastAPIClient.get<FiCastAPIResponse>(`/podcast/${task_id}/script`);
    const podcast = podcastScriptResponse.data;

    const messages = convertDialoguesToMessages(podcast.dialogues);

    // Update weatherUI with the final podcast content
    weatherUI.update(<MessageDisplay messages={messages} />);
    weatherUI.done(); // Mark as done
  } catch (error: any) {
    console.error("Error fetching podcast:", error);
    weatherUI.update(<div className="text-red-500">Failed to load podcast messages: {error.message}</div>);
    weatherUI.done(); // Ensure it's marked as done even on error
    return { ui: null, error: `Failed to load podcast messages: ${error.message}` };
  }
};
