"use client";

import { useState } from "react";
import { Landing } from "@/app/(components)/landing";
import { Podcast } from "@/app/(components)/podcast";
import { getPodcast } from "./actions/podcast_ui";
import { SAMPLE_MESSAGES } from "@/app/(components)/samples";

import { PodcastData } from "@/app/models/podcast";
import { Participant } from "@/app/models/particpants";

export default function Home() {
  const [data, setData] = useState<PodcastData | null>(null);
  const [podcastContent, setPodcast] = useState<JSX.Element | JSX.Element[] | null>(null); // Allow single element or array
  const [showPodcast, setShowPodcast] = useState<boolean>(false); // podcast visibility
  const [showModal, setShowModal] = useState<boolean>(false); // modal


  const handleStart = async (data: PodcastData) => {
    console.log("Podcast data received:", data);
    
    if (data.participants.length > 2) {
      // Show modal if more than 2 participants are selected
      setShowModal(true);
      return;
    }
    
    if (!data.participants || data.participants.length === 0) {
      console.warn("No participants selected. Showing sample messages.");
      // Show SAMPLE_MESSAGES if no participants are selected
      const podcastUi = SAMPLE_MESSAGES.map((msg, idx) => (
        <div key={idx} className="p-4">
          <h3 className="font-bold">{msg.name}</h3>
          <p>{msg.message}</p>
        </div>
      ));
      setPodcast(podcastUi);
      setData(data);
      setShowPodcast(true); // Show podcast view
      return;
    }

    // Fetch podcast content
    // Ensure this is a tuple with at least one speaker
    console.log("Fetching podcast content...");
    const podcastUi = await getPodcast(
      data.topic, data.participants 
      
    );
    setPodcast(podcastUi);
    setData(data);
    setShowPodcast(true); // Show podcast view
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
      {/* Modal for premium plan notification */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-black p-8 rounded-lg text-center">
            <h2 className="modal-header">Creative Premium Required</h2>
            <p>You need a <b>creative premium</b> plan to select more than 2 participants.<br></br>
            Join us at the minimum cost to support our project and use all the features.</p>
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
