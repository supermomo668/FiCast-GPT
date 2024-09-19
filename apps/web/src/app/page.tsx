"use client";

import { useState } from "react";

import { Landing } from "@/app/(components)/landing";
import { Podcast } from "@/app/(components)/podcast";
import { createPodcastScript, fetchPodcastScript } from './actions/backend_message';
import { fetchStatus } from "./actions/task_status";

import { SAMPLE_PODCAST } from "@/app/(components)/samples";
import { MessageDisplay } from "@/app/(components)/Message";
import { convertDialoguesToMessages } from "@/app/utils/messageConverter";
import { PodcastUIProps } from "@/app/models/podcast";
import { PodcastRequestData } from "@/app/models/api_entry";

export default function Home() {
  const [loading, setLoading] = useState<boolean>(false);
  const [taskStatus, setTaskStatus] = useState<string | null>(null);
  const [podcastContent, setPodcastContent] = useState<JSX.Element | JSX.Element[] | null>(null);
  const [showPodcast, setShowPodcast] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMessage, setModalMessage] = useState<JSX.Element | string>("");

  const openModal = (message: JSX.Element | string) => {
    setModalMessage(message);
    setShowModal(true);
  };

  const renderPodcastUI = ({
    topic,
    abstract = "",
    participants,
    messages,
  }: PodcastUIProps) => {
    const podcastUi = (
      <Podcast topic={topic} abstract={abstract} participants={participants} onClose={() => setShowPodcast(false)}>
        {messages}
      </Podcast>
    );
    setPodcastContent(podcastUi);
    setShowPodcast(true);
  };

  const handleInvalidSelection = () => {
    const sampleMessages = convertDialoguesToMessages(SAMPLE_PODCAST.dialogues);
    openModal(
      <>
        <h2 className="modal-header">Invalid Selection (OK!)</h2>
        <p>You usually need 2 people to have a conversation 😅 <br /> We're showing you a sample conversation from the app.</p>
      </>
    );
    renderPodcastUI({
      topic: SAMPLE_PODCAST.title,
      participants: SAMPLE_PODCAST.participants,
      messages: <MessageDisplay messages={sampleMessages} />,
    });
  };
  
  const handleStart = async (data: PodcastRequestData) => {
    const totalParticipants = data.participants.length;

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

    if (!data.participants || totalParticipants < 2) {
      handleInvalidSelection();
      return;
    }

    console.log("Fetching podcast messages with data: ", data);

    setLoading(true);
    setTaskStatus("Generating Script...");

    try {
      // Step 1: Fetch the podcast task
      const { task_id } = await createPodcastScript(data);
      console.log("Podcast task created:", task_id);
      setTaskStatus("Task created, awaiting script generation...");

      // Step 2: Poll for the task status until script creation is complete
      const status = await fetchStatus(task_id, "script");
      
      if (status.script_status?.toLowerCase() === 'script_created') {
        // Step 3: Fetch the final podcast script once status is SCRIPT_CREATED
        const podcast = await fetchPodcastScript(task_id);
        const messages = convertDialoguesToMessages(podcast.dialogues);

        renderPodcastUI({
          topic: data.topic,
          abstract: podcast.abstract,
          participants: podcast.participants,
          messages: <MessageDisplay messages={messages} />,
        });
      } else {
        throw new Error("Script generation failed.");
      }
    } catch (error) {
      console.error("Error during podcast creation:", error);
      openModal("Failed to create the podcast.");
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 text-white bg-gradient-to-b bg-slate-900 from-slate-900 to-purple-900/30">
      {!showPodcast && <Landing onStart={handleStart} />}

      {loading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
          <div className="spinner" />
          <p>{taskStatus}</p>
        </div>
      )}

      {showPodcast && podcastContent}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-black p-8 rounded-lg text-center">
            {modalMessage}
            <button className="mt-4 px-4 py-2 bg-purple-600 text-white rounded" onClick={() => setShowModal(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
