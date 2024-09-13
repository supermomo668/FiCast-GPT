import { PodcastProps } from "@/app/models/podcast";

/**
 * The Podcast component renders a podcast with a topic, abstract, participants, 
 * and main content. It also includes a stylish close button at the top right 
 * corner.
 * 
 * @param topic The topic of the podcast.
 * @param abstract A short summary of the podcast.
 * @param participants Information about the participants, including their names 
 * and roles.
 * @param children The main content of the podcast, which is usually a list of 
 * messages.
 * @param onClose A function to call when the close button is clicked. If not 
 * provided, the close button will not be rendered.
 * 
 * @returns A JSX element representing a podcast.
 */
export function Podcast({ 
  topic, abstract, participants, children, onClose 
}: PodcastProps) {
  
  if (!participants || !topic) {
    return null;
  }
  const intl = new Intl.ListFormat("en", {
    style: "long", type: "conjunction",
  });
  // Get Names for displaying
  const hostNames = intl.format(participants.hosts.map((host) => host.name));
  const guestNames = intl.format(participants.guests.map((guest) => guest.name));
  console.log("Podcast rendered. Hosted by:", hostNames, "with guests:", guestNames);
  return (
    <div className="relative flex flex-col h-screen w-full max-w-4xl mx-auto bg-gradient-to-b from-gray-900 to-purple-900 rounded-2xl shadow-2xl text-white overflow-hidden">
      {/* Stylish & Futuristic Close Button */}
      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-10 h-10 border border-purple-400 rounded-lg hover:bg-purple-600 hover:border-purple-600 transition-colors flex items-center justify-center text-xl text-white hover:text-red-400"
        >
          ✕
        </button>
      )}

      {/* Podcast Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-900 text-white px-8 py-6 flex items-center justify-between shadow-md">
        <div>
          <h2 className="text-3xl font-bold mb-1">Topic: {topic}</h2>
          <p className="text-sm text-purple-200">
            Hosted by {hostNames}{guestNames ? ` with guests ${guestNames}` : ""}
          </p>
        </div>
      </div>

      {/* Podcast Abstract */}
      {abstract && (
        <div className="bg-purple-800 text-purple-200 px-8 py-4">
          <h3 className="text-lg font-semibold">Summary</h3>
          <p className="text-sm italic">{abstract}</p>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-8 bg-gray-900 text-gray-100 space-y-4">
        {children}
      </div>
    </div>
  );
}