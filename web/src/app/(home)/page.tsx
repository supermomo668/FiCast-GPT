"use client";

import { Landing } from "@/app/components/landing";
import { Podcast, SAMPLE_MESSAGES } from "@/app/components/podcast";
import Image from "next/image";
import { useState } from "react";
import { getPodcast } from "../actions";

export default function Home() {
  const [data, setData] = useState<{ topic: string; speakers: string[] }>();
  const [podcastContent, setPodcast] = useState<any>(null);
  const [useOpenai, setOpenai] = useState(true);

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
          onStart={async (data) => {
            const podcastUi = await getPodcast(
              data.topic,
              data.speakers,
              useOpenai
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
