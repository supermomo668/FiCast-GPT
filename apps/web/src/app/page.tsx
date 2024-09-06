// src/app/(home)/page.tsx
"use client";

import { Landing } from "@/app/(components)/landing";
import { Podcast } from "@/app/(components)/podcast";
import Image from "next/image";
import { useState } from "react";
import { getPodcast } from "@/app/actions";

interface PodcastData {
  topic: string;
  speakers: string[];
}


export default function Home() {
  const [data, setData] = useState<PodcastData | null>(null);
  const [podcastContent, setPodcast] = useState<any>(null);
  // const [useOpenai, setOpenai] = useState(true);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between  p-24 text-white bg-gradient-to-b bg-slate-900 from-slate-900 to-purple-900/30">
      {/* <label className="text-xs fixed top-2 right-4 accent-purple-500 text-slate-300 ">
        Use OpenAI directly{" "}
        <input
          className="align-center"
          checked={useOpenai}
          type="checkbox"
          onChange={() => setOpenai((current) => !current)}
        />
      </label> */}

      {!data && (
        <Landing
          onStart={async (data: PodcastData) => {
            // Ensure speakers array is not empty
            if (data.speakers.length === 0) {
              throw new Error("Speakers array must contain at least one speaker.");
            }
            const podcastUi = await getPodcast(
              data.topic,
              data.speakers as [string, ...string[]],  // Type assertion to enforce tuple type
              // useOpenai
            );
            setPodcast(podcastUi);
            setData(data);
          }}
        />
      )}
      {data && (
        <Podcast topic={data?.topic} speakers={data?.speakers || []}>
          {podcastContent}
        </Podcast>
      )}
    </main>
  );
}
