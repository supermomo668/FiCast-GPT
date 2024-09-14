"use server";

import { FicastAPIClient } from '@/lib/ficast_client';

import { MessageEntryUI } from "@/app/models/messages";
import { FiCastAPIResponse, PodcastRequestData, TaskCreateResponse, TaskStatusResponse } from "@/app/models/api_entry";
import { convertDialoguesToMessages } from "@/app/utils/messageConverter"; // Import the utility function

export async function createPodcastScript({
  topic,
  n_rounds = 10,
  participants,
}: PodcastRequestData): Promise<{ task_id: string }> {
  console.log('Sending podcast create request...');
  
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

  try {
    // Post request to create a podcast
    const podcastCreateResponse = await FicastAPIClient.post<TaskCreateResponse>('/podcast/create', requestBody);
    // Extract task ID from response
    const createData: TaskCreateResponse = podcastCreateResponse.data;
    const taskId = createData.task_id;
    console.log('Received Task ID:', taskId);
    return { task_id: taskId };
  } catch (error) {
    console.error('Error creating podcast task:', error);
    throw error;
  }
}

// Function to check the status of the task until it's completed
export async function waitTaskComplete(taskId: string): Promise<TaskStatusResponse> {
  let isCompleted = false;
  let statusResponse: TaskStatusResponse | null = null;
  try {
    // Keep polling until the task is complete (SCRIPT_CREATED)
    while (!isCompleted) {
      const response = await FicastAPIClient.get<TaskStatusResponse>(`/podcast/${taskId}/status`);
      statusResponse = response.data;
      console.log('Polling task status:', response.data);
      if (!statusResponse) {
        console.error('Error: statusResponse is null or undefined');
        throw new Error('statusResponse is null or undefined');
      }

      // Add a return statement here
      if (statusResponse.script_status.toLowerCase() === 'script_created') {
        isCompleted = true;
        return statusResponse;
      } else {
        // Wait for 2 seconds before polling again
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
    }
  } catch (error) {
    console.error('Error polling task status:', error);
    throw error;
  }
  return statusResponse as TaskStatusResponse;
}

export async function getMessagesNewBackend({
  topic, participants, n_rounds=10}: PodcastRequestData, setLoading: (loading: boolean) => void
): Promise<MessageEntryUI[]> {
  const podcast_request: PodcastRequestData = {
    topic: topic, n_rounds: n_rounds, participants: participants,
  }
  const task = await createPodcastScript(podcast_request);
  console.log("getMessagesNewBackend: Data received from fetchPodcastScript:", task.task_id);
  const status_update = await waitTaskComplete(task.task_id);
  // Fetch the final script data when completed
  const finalResponse = await FicastAPIClient.get<FiCastAPIResponse>(`/podcast/${task.task_id}/script`);
  const messages: MessageEntryUI[] = convertDialoguesToMessages(finalResponse.data.dialogues);
  console.log("getMessagesNewBackend: Converted messages:", messages);

  return messages;
}