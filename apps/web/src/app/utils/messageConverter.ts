import { MessageEntryUI } from "@/app/models/messages";
import { Dialogues } from "@/app/models/podcast";


  /**
   * Converts a list of dialogue entries into a list of message entries.
   */
export function convertDialoguesToMessages(dialogues: Dialogues): MessageEntryUI[] {
  return dialogues.map((entry) => ({
    id: Math.random().toString(32).substring(2), // Random unique ID
    name: entry.speaker.name, // Use the speaker's name
    message: entry.dialogue.trim(), // Extract and trim the dialogue
    thought: entry.thought?.trim() || "", // Handle thought if it exists
  }));
}