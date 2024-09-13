"use client";

import { useState } from "react";

import { Landing } from "@/app/(components)/landing";
import { Podcast } from "@/app/(components)/podcast";
import { getPodcast } from "./actions/podcast_ui";
import { SAMPLE_PODCAST } from "@/app/(components)/samples";
import { MessageDisplay } from "@/app/(components)/Message";
import { convertDialoguesToMessages } from "@/app/utils/messageConverter";
import { PodcastUIProps } from "@/app/models/podcast";
import { PodcastRequestData } from "@/app/models/api_entry";


export default function Home() {
  const [podcastContent, setPodcastContent] = useState<JSX.Element | JSX.Element[] | null>(null);
  const [showPodcast, setShowPodcast] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMessage, setModalMessage] = useState<JSX.Element | string>("");

  // Helper function to open the modal with a message
  const openModal = (message: JSX.Element | string) => {
    setModalMessage(message);
    setShowModal(true);
  };

  // Function to render the podcast UI based on the provided data
  const renderPodcastUI = ({
    topic,
    abstract = "",
    participants,
    messages,
  }: PodcastUIProps) => {
    const podcastUi = (
      <Podcast topic={topic} abstract={abstract} participants={participants} 
      onClose={() => setShowPodcast(false)}
      >
        {messages}
      </Podcast>
    );
    setPodcastContent(podcastUi);
    setShowPodcast(true);
  };

  // Function to handle invalid selection and show the sample podcast
  const handleInvalidSelection = () => {
    const sampleMessages = convertDialoguesToMessages(SAMPLE_PODCAST.dialogues);
    openModal(
      <>
        <h2 className="modal-header">Invalid Selection (OK!)</h2>
        <p> You usually need 2 people to have a conversation 😅 <br /> We're showing you a sample conversation from the app. </p>
      </>
    );
    renderPodcastUI({
      topic:SAMPLE_PODCAST.topic, 
      participants: SAMPLE_PODCAST.participants, 
      messages: <MessageDisplay messages={sampleMessages} />
    });
  };

  // Main function to handle starting the podcast
  const handleStart = async (data: PodcastRequestData) => {
    const totalParticipants = data.participants.length;

    // Condition 1: More than 2 participants (premium required)
    if (totalParticipants > 2) {
      openModal(
        <>
          <h2 className="modal-header">Creative Premium Required</h2>
          <p>
            You need a <b>creative premium</b> plan to have group talks!<br />
            Join us at the minimum cost to support our project and use all the features.
          </p>
        </>
      );
      return;
    }

    // Condition 2: Invalid selection, use SAMPLE_PODCAST
    if (!data.participants || totalParticipants < 2) {
      handleInvalidSelection();
      return;
    }

    // Condition 3: Valid selection, fetch podcast content
    console.log("Fetching podcast messages with podcast data: ", data);
    const podcastUi = await getPodcast(data);
    setPodcastContent(podcastUi);
    setShowPodcast(true);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 text-white bg-gradient-to-b bg-slate-900 from-slate-900 to-purple-900/30">
      {/* Render the homepage (Landing) if the podcast is not showing */}
      {!showPodcast && <Landing onStart={handleStart} />}

      {/* Render the podcast view if showPodcast is true */}
      {showPodcast && podcastContent}

      {/* Centralized Modal for conditions */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-black p-8 rounded-lg text-center">
            {modalMessage}
            <button
              className="mt-4 px-4 py-2 bg-purple-600 text-white rounded"
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
