"use client";

import { cn } from "@/lib/utils";
import { useState } from "react";
import { CHARACTERS } from "./CHARACTERS";

const MAX_CHARACTERS = 10;

export function CharacterSelector({ onChange }) {
  const [selected, setSelected] = useState<Set<string>>(new Set());

  function buttonHandler(name: string) {
    return () => {
      if (selected.has(name)) {
        const newSelected = new Set(selected);
        newSelected.delete(name);
        setSelected(newSelected);
        onChange(newSelected.values());
        return;
      }

      if (selected.size === MAX_CHARACTERS) {
        return;
      }

      const newSelected = new Set(selected);
      newSelected.add(name);
      setSelected(newSelected);
      onChange(newSelected.values());
    };
  }

  return (
    <div className="grid grid-cols-3 gap-8">
      {CHARACTERS.map((ch) => {
        return (
          <button
            onClick={buttonHandler(ch.name)}
            key={ch.name}
            className={cn(
              "border-2 border-solid p-3 rounded-2xl",
              selected.has(ch.name)
                ? "border-white bg-gradient-to-r from-purple-500 to-purple-900"
                : "border-transparent"
            )}
          >
            <img src={ch.image} alt={ch.name} height="80" />
            <br />
            <span className="text-xs">{ch.name}</span>
          </button>
        );
      })}
    </div>
  );
}

export function Landing({ onStart }) {
  const [topic, setTopic] = useState<string>("<An interesting topic>");
  const [speakers, setSpeakers] = useState<string[]>();

  return (
    <div className="max-w-screen-md text-center">
      <header className="text-center">
        <h1 className="text-6xl font-extrabold">Fantasy Podcast</h1>
        <h2 className="text-xl mt-8">Pick your participants</h2>
      </header>
      <CharacterSelector onChange={setSpeakers} />
      <section className="text-center mb-8 mt-8">
        <h2 className="text-xl">Choose your topic</h2>
        <input
          className="text-lg py-2 px-4 text-white bg-transparent border-b-white border-b focus:border-b-2 focus:outline-none"
          value={topic}
          onChange={(evt) => setTopic(evt.target.value)}
        ></input>
      </section>

      <button
        className="bg-transparent hover:bg-purple-500 text-purple-200 font-semibold hover:text-white py-2 px-4 border border-purple-200 hover:border-transparent rounded"
        onClick={() => onStart({ topic, speakers })}
      >
        Start Podcast
      </button>
    </div>
  );
}
