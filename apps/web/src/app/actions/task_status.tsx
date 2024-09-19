"use server";
import axios, { AxiosError } from "axios";
import { TaskStatusResponse, TaskProgressRequest } from "@/app/models/api_entry";
import { FicastAPIClient } from "@/lib/ficast_client";

// Polling mechanism to handle progress over POST for streaming-like behavior
export const fetchStatus = async (
  task_id: string,
  event_type: "script" | "audio" = "script"
): Promise<TaskStatusResponse> => {
  let isCompleted = false;
  let statusResponse: TaskStatusResponse | null = null;
  const taskProgressRequestBody: TaskProgressRequest = {
    task_id: task_id,
    event_type: event_type,
  };
  console.log("Polling task status for task_id:", task_id);
  // Continue polling until the task is completed
  while (!isCompleted) {
    try {
      // Send a POST request to the server to get task progress updates
      const response = await FicastAPIClient.post<TaskStatusResponse>(
        "/podcast/status", // POST request to fetch progress updates
        taskProgressRequestBody
      );
      console.log("Polling task status:", response.data);
      statusResponse = response.data;

      // Log the response for debugging
      console.log("Received task progress response:", statusResponse);

      // Check if the script/audio is created
      if (
        statusResponse.script_status?.toLowerCase() === "script_created"
      ) {
        isCompleted = true;
        return statusResponse;
      }

      // Wait for 2 seconds before making another request
      await new Promise((resolve) => setTimeout(resolve, 2000));

    } catch (error) {
      console.error("Error polling task status:", error);
      throw error;
    }
  }

  return statusResponse!;
};
