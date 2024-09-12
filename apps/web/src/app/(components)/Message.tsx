import { MessageEntry, MessageType } from "@/app/models/messages";
import { LANDING_CHARACTERS, CUSTOM } from "@/app/(components)/CHARACTERS"; // Import CHARACTERS directly

export function Message({ message }: { message: MessageEntry }) {
  // Find the character's image based on the message name
  const character = LANDING_CHARACTERS.find((ch) => ch.name === message.name);

  return (
    <div className="flex items-start gap-6 mb-6 text-white">
      {/* Avatar */}
      <div className="w-16 h-16 rounded-full overflow-hidden flex-shrink-0">
        <img className="object-cover w-full h-full" src={character?.image || CUSTOM.image } alt={message.name} />
      </div>

      {/* Speaker and Message */}
      <div className="grid gap-2 items-start text-sm">
        {/* Speaker Name */}
        <div className="flex items-center gap-2">
          <span className="text-lg font-extrabold tracking-wide text-purple-300">{message.name}</span>
        </div>
        {/* Dialogue */}
        <div className="text-md font-light text-gray-200 leading-relaxed">
          <p>{message.message}</p>
        </div>

        {/* Inner Thought */}
        {message.thought && (
          <div className="text-sm text-purple-400 italic">
            <p>Inner Thought: {message.thought}</p>
          </div>
        )}
      </div>
    </div>
  );
}


// Component to handle displaying messages with inner thoughts
function MessageWithThoughts({ message, speaker, thought }: { message: string; speaker: string; thought?: string }) {
  return (
    <div className="mb-6">
      <p className="text-lg font-semibold text-white">{speaker}: {message}</p>
      {thought && (
        <p className="text-sm text-purple-300 italic">Inner Thought: {thought}</p>
      )}
    </div>
  );
};

interface MessageDisplayProps {
  messages: MessageType[];
}

export function MessageDisplay({ messages }: MessageDisplayProps) {
  return (
    <div>
      {messages.map((msg: MessageType) => (
        <Message
          key={msg.id}
          message={{
            name: msg.name,
            message: msg.message,
            thought: msg.thought,
          }}
        />
      ))}
    </div>
  );
}
