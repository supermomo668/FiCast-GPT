"use client";

import { useState } from "react";
import { Landing } from "@/app/(components)/landing";
import { Podcast } from "@/app/(components)/podcast";
import { getPodcast } from "./actions/podcast_ui";
import { SAMPLE_MESSAGES } from "@/app/(components)/samples";
import { MessageDisplay } from "@/app/(components)/Message";

import { MessageType } from "@/app/models/messages";
import { PodcastData } from "@/app/models/podcast";

export default function Home() {
  const [data, setData] = useState<PodcastData | null>(null);
  const [podcastContent, setPodcast] = useState<JSX.Element | JSX.Element[] | null>(null); // Allow single element or array
  const [showPodcast, setShowPodcast] = useState<boolean>(false); // podcast visibility
  const [showModal, setShowModal] = useState<boolean>(false); // modal visibility
  const [modalMessage, setModalMessage] = useState<JSX.Element | string>(""); // modal message content

  const handleStart = async (data: PodcastData) => {
    console.log("Podcast data received:", data);

    // Check if more than 2 participants are selected
    if ((data.participants.guests.length + data.participants.hosts.length) > 2) {
      setModalMessage(
        <>
          <h2 className="modal-header">Creative Premium Required</h2>
          <p>You need a <b>creative premium</b> plan to have group talks!<br/>Join us at the minimum cost to support our project and use all the features.</p>
        </>
      );
      setShowModal(true);
      return;
    }

    // Invalid Selection: Check if no participants or fewer than 2 are selected
    if (!data.participants || data.participants.hosts.length < 1 || (data.participants.guests.length + data.participants.hosts.length ) < 2) {
      console.warn("No participants selected. Showing sample messages.");
      setModalMessage(
        <>
          <h2 className="modal-header">Invalid Selection (OK)</h2>
          <p>You usually need 2 people to have a conversation😅 <br></br>We're showing you a sample conversation that came from the app</p>
        </>
      );
      setShowModal(true);

      // Use MessageDisplay for SAMPLE_MESSAGES
      const sampleMessages: MessageType[] = SAMPLE_MESSAGES.map((msg, idx) => ({
        id: `${idx}`,
        name: msg.name,
        message: msg.message,
        thought: '',
      }));
      const podcastUi = <MessageDisplay messages={sampleMessages} />;
      setPodcast(podcastUi);
      setData(data);
      setShowPodcast(true); // Show podcast view
      return;
    } else {
      // Fetch the podcast content if the correct number of participants are selected
      console.log("Fetching podcast content...");
      const podcastUi = await getPodcast(
        data.topic, data.participants);
      setPodcast(podcastUi);
      setData(data);
      setShowPodcast(true); // Show podcast view
    }
  };

  const handleClosePodcast = () => {
    setShowPodcast(false); // Hide podcast view when "X" is clicked
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 text-white bg-gradient-to-b bg-slate-900 from-slate-900 to-purple-900/30">
      {/* Render the homepage (Landing) if the podcast is not showing */}
      {!showPodcast && <Landing onStart={handleStart} />}

      {/* Render the podcast view if showPodcast is true */}
      {showPodcast && data && (
        <Podcast
          topic={data?.topic}
          speakers={data?.participants.map((p) => p.name)}
          onClose={handleClosePodcast} // Pass close handler to Podcast component
        >
          {podcastContent}
        </Podcast>
      )}

      {/* Centralized Modal for conditions */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-black p-8 rounded-lg text-center">
            {modalMessage}
            <button
              className="mt-6 bg-purple-500 text-white px-4 py-2 rounded"
              onClick={() => setShowModal(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
