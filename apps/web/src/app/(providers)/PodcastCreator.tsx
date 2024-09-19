"use client";

import { useState } from "react";
import { Landing } from "@/app/(components)/landing";
import { getPodcast } from "@/app/actions/podcast_ui";
import { PodcastRequestData } from "@/app/models/api_entry";

export default function PodcastCreator() {
  const [loading, setLoading] = useState<boolean>(false);
  const [taskStatus, setTaskStatus] = useState<string | null>(null);
  const [podcastContent, setPodcastContent] = useState<JSX.Element | JSX.Element[] | null>(null);
  const [showPodcast, setShowPodcast] = useState<boolean>(false);

  const handleStart = async (data: PodcastRequestData) => {
    setLoading(true);
    setTaskStatus("Starting podcast creation...");

    try {
      const result = await getPodcast(data);
      setLoading(false);

      if (result?.error) {
        console.error("Task error:", result.error);
        setTaskStatus(result.error);
      } else if (result?.ui) {
        setTaskStatus(null); // Clear task status
        setPodcastContent(result.ui);
        setShowPodcast(true);
      } else {
        console.error("Error fetching podcast data");
      }
    } catch (error: any) {
      setLoading(false);
      setTaskStatus(`Error during podcast creation: ${error.message}`);
      console.error("Error during podcast creation:", error);
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
    </main>
  );
}
