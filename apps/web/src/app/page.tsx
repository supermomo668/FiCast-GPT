"use client";

import { useState } from "react";
import { Landing } from "@/app/(components)/landing";
import { getPodcast } from "./actions/podcast_ui";
import { PodcastRequestData } from "@/app/models/api_entry";

export default function Home() {
  const [loading, setLoading] = useState<boolean>(false);
  const [taskStatus, setTaskStatus] = useState<string | null>(null); // Task status state
  const [podcastContent, setPodcastContent] = useState<JSX.Element | JSX.Element[] | null>(null);
  const [showPodcast, setShowPodcast] = useState<boolean>(false);

  // Function to start podcast creation
  const handleStart = async (data: PodcastRequestData) => {
    setLoading(true);
    setTaskStatus("Starting podcast creation...");
  
    // Fetch the podcast content with real-time updates
    const result = await getPodcast(data);
    setLoading(false);
  
    if (result?.error) {
      console.error('Task error:', result.error);
      setTaskStatus(result.error);
    } else if (result?.ui) {
      setTaskStatus(null); // Clear task status
      setPodcastContent(result.ui);
      setShowPodcast(true);
    } else {
      console.error('Error fetching podcast data');
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 text-white bg-gradient-to-b bg-slate-900 from-slate-900 to-purple-900/30">
      {!showPodcast && <Landing onStart={handleStart} />}

      {/* Loading Spinner and Status */}
      {loading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
          {/* Spinner component */}
          <div className="spinner" />
          <p>{taskStatus}</p>
        </div>
      )}

      {/* Render the podcast view if showPodcast is true */}
      {showPodcast && podcastContent}
    </main>
  );
}
