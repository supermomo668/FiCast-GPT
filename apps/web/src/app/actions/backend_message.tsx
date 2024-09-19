"use server";

import { FicastAPIClient } from '@/lib/ficast_client';
import { MessageEntryUI } from "@/app/models/messages";
import { FiCastAPIResponse, PodcastRequestData, TaskCreateResponse, TaskStatusResponse } from "@/app/models/api_entry";
import { convertDialoguesToMessages } from "@/app/utils/messageConverter"; 
import { AxiosError } from 'axios';

// Log statement to trace the function execution
console.log("backend_message.tsx is loaded");

// Function to create a podcast and return the task ID
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
    const podcastCreateResponse = await FicastAPIClient.post<TaskCreateResponse>('/podcast/create-script', requestBody);
    const createData: TaskCreateResponse = podcastCreateResponse.data;
    const taskId = createData.task_id;
    return { task_id: taskId };
  } catch (error) {
    console.error('Error creating podcast task:', error);
    throw error;
  }
}

// Fetch the podcast script by making a POST request
export async function fetchPodcastScript(task_id: string): Promise<FiCastAPIResponse> {
  try {
    const podcastRequestBody = { task_id: task_id };
    const podcastScriptResponse = await FicastAPIClient.post<FiCastAPIResponse>(
      '/podcast/script',
      podcastRequestBody
    );
    return podcastScriptResponse.data;
  } catch (error) {
    console.error('Error fetching podcast script:', error);
    throw new Error('Failed to fetch podcast script.');
  }
}