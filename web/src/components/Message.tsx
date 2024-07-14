import { MessageEntry, CharacterImages } from "./podcast";

export function Message({ message }: { message: MessageEntry }) {
  return (
    <div className="flex items-start gap-4 text-black">
      <div className="text-3xl flex-shrink-0 flex items-center justify-center w-20">
        <img className="h-full" src={CharacterImages.get(message.name)} />
      </div>
      <div className="grid gap-1 items-start text-sm">
        <div className="flex items-center gap-2">
          <div className="font-bold">{message.name}</div>
          {/* <div className="text-sm text-muted-foreground">10:32 AM</div> */}
        </div>
        <div>
          <p>{message.message}</p>
        </div>
      </div>
    </div>
  );
}
