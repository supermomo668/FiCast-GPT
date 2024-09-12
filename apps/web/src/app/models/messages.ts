// Define the shape of message objects returned by the backend

export interface MessageType {
  id: string;
  name: string;
  message: string;
  thought: string;
}

export type MessageEntry = {
  name: string;
  message: string;
  thought: string;
};