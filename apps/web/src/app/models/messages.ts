// Define the shape of message objects returned by the backend
export interface MessageUI {
  name: string;
  message: string;
  thought: string;
}

export interface MessageEntryUI extends MessageUI {
  id: string;
}